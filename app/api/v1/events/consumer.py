import json
import aio_pika
from datetime import datetime, timezone
from app.core.database import Neo4jDB, MongoDB
from app.api.v1.events.models import EventModel
from app.core.config import settings

async def process_event():
    """
    Background worker to consume events from RabbitMQ and store them in Neo4j.
    """
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("event_queue", durable=True)

        async for message in queue:
            async with message.process():
                event_data = json.loads(message.body)
                await store_event_in_neo4j(EventModel(**event_data))

async def store_event_in_neo4j(event: EventModel):
    """
    Stores an event in Neo4j and links it sequentially in the session's event chain.
    """
    neo4j_driver = Neo4jDB.driver
    mongo_db = MongoDB.get_db()

    session_id = event.session_id
    app_id = event.app_id
    event_id = event.event_id
    event_type = event.event_type
    timestamp = event.timestamp.isoformat()
    payload = event.payload

    # Ensure session exists in MongoDB (for referencing in APIs)
    session = await mongo_db.sessions.find_one({"session_id": session_id})
    if not session:
        await mongo_db.sessions.insert_one({"session_id": session_id, "app_id": app_id})

    # Convert datetime objects in payload to strings
    def serialize_payload(data):
        if isinstance(data, dict):
            return {k: serialize_payload(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [serialize_payload(i) for i in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        return data

    serialized_payload = serialize_payload(payload)

    # Store event in Neo4j and braid it in session flow
    query = """
    MERGE (s:Session {session_id: $session_id})
    ON CREATE SET s.app_id = $app_id

    WITH s
    OPTIONAL MATCH (s)-[:LAST_EVENT]->(last_event:Event)

    CREATE (new_event:Event {
        event_id: $event_id,
        event_type: $event_type,
        timestamp: $timestamp,
        payload: $payload
    })

    FOREACH (_ IN CASE WHEN last_event IS NULL THEN [1] ELSE [] END |
        CREATE (s)-[:HAS_EVENT]->(new_event)
    )

    FOREACH (_ IN CASE WHEN last_event IS NOT NULL THEN [1] ELSE [] END |
        CREATE (last_event)-[:NEXT]->(new_event)
    )

    WITH s, new_event
    OPTIONAL MATCH (s)-[old_last_event:LAST_EVENT]->(prev_event:Event)
    DELETE old_last_event
    MERGE (s)-[:LAST_EVENT]->(new_event)
    """

    async with neo4j_driver.session() as neo4j_session:
        result = await neo4j_session.run(
            query,
            session_id=session_id,
            app_id=app_id,
            event_id=event_id,
            event_type=event_type,
            timestamp=timestamp,
            payload=json.dumps(serialized_payload),
        )

        summary = await result.consume()
        if summary.counters.nodes_created > 0:
            print(f"Event {event_id} successfully stored and linked in Neo4j.")
        else:
            print(f"Failed to store event {event_id} in Neo4j.")
