from fastapi import HTTPException
from app.core.database import Neo4jDB

class EventQueries:
    @staticmethod
    async def get_event_flow(session_id: str):
        """
        Retrieve the full event sequence for a session in correct order.
        """
        query = """
        MATCH (s:Session {session_id: $session_id})-[:HAS_EVENT]->(first_event:Event)
        OPTIONAL MATCH path = (first_event)-[:NEXT*]->(next_events)
        WITH first_event, next_events
        UNWIND [first_event] + next_events AS event
        RETURN event ORDER BY event.timestamp
        """

        async with Neo4jDB.driver.session() as session:
            result = await session.run(query, session_id=session_id)
            records = await result.data()

            if not records:
                raise HTTPException(status_code=404, detail="No events found for this session.")

            # Extract and order the events properly
            events = []
            for record in records:
                event = record["event"]
                if event is None:
                    continue  # Skip empty records

                events.append({
                    "event_id": event["event_id"],
                    "event_type": event["event_type"],
                    "timestamp": event["timestamp"],
                    "payload": event["payload"],
                    "next_event": None  # Will be assigned below
                })

            # Assign `next_event` by linking each event in order
            for i in range(len(events) - 1):
                events[i]["next_event"] = events[i + 1]["event_id"]

            return {"session_id": session_id, "events": events}
    
    @staticmethod
    async def get_latest_event(session_id: str):
        """
        Retrieve the latest event in a session (real-time tracking).
        """
        query = """
        MATCH (s:Session {session_id: $session_id})-[:LAST_EVENT]->(latest:Event)
        RETURN latest
        """

        async with Neo4jDB.driver.session() as session:
            result = await session.run(query, session_id=session_id)
            record = await result.single()
            if not record:
                raise HTTPException(status_code=404, detail="No latest event found.")
            
            latest_event = record["latest"]
            return {
                "event_id": latest_event["event_id"],
                "event_type": latest_event["event_type"],
                "timestamp": latest_event["timestamp"],
                "payload": latest_event["payload"]
            }
        
    @staticmethod
    async def get_event_counts(session_id: str):
        """
        Count the occurrences of each event type in a session.
        """
        query = """
        MATCH (s:Session {session_id: $session_id})-[:HAS_EVENT]->(e:Event)
        RETURN e.event_type AS event_type, COUNT(e) AS count
        """

        async with Neo4jDB.driver.session() as session:
            result = await session.run(query, session_id=session_id)
            counts = {record["event_type"]: record["count"] async for record in result}

        if not counts:
            raise HTTPException(status_code=404, detail="No events found for analytics.")

        return {"session_id": session_id, "event_counts": counts}
    
    @staticmethod
    async def get_conversion_funnel(session_id: str, steps: list):
        """
        Analyzes conversion rates across a series of events in a session.
        Example: ["page_view", "add_to_cart", "checkout"]
        """
        query = """
        MATCH (s:Session {session_id: $session_id})-[:HAS_EVENT]->(e:Event)
        WHERE e.event_type IN $steps
        RETURN e.event_type AS step, COUNT(e) AS count
        """

        async with Neo4jDB.driver.session() as session:
            result = await session.run(query, session_id=session_id, steps=steps)
            funnel_data = {record["step"]: record["count"] async for record in result}

        if not funnel_data:
            raise HTTPException(status_code=404, detail="No funnel data found.")

        # Order the results based on the order in `steps`
        ordered_funnel = {step: funnel_data.get(step, 0) for step in steps}

        return {"session_id": session_id, "funnel": ordered_funnel}
    
    @staticmethod
    async def get_retention_rate(days: int):
        """
        Calculates user retention rate over a time period.
        """
        query = """
        MATCH (s:Session)-[:HAS_EVENT]->(e:Event)
        WHERE datetime(e.timestamp) >= datetime() - duration({days: $days})
        RETURN COUNT(DISTINCT s.session_id) AS active_sessions
        """

        async with Neo4jDB.driver.session() as session:
            result = await session.run(query, days=days)
            record = await result.single()

        if not record:
            raise HTTPException(status_code=404, detail="No retention data found.")

        return {"days": days, "active_sessions": record["active_sessions"]}
    
    @staticmethod
    async def get_session_heatmap():
        """
        Analyzes user activity distribution across different hours of the day.
        """
        query = """
        MATCH (e:Event)
        RETURN datetime(e.timestamp).hour AS hour, COUNT(e) AS event_count
        ORDER BY hour
        """

        async with Neo4jDB.driver.session() as session:
            result = await session.run(query)
            heatmap = {str(record["hour"]): record["event_count"] async for record in result}

        if not heatmap:
            raise HTTPException(status_code=404, detail="No heatmap data found.")

        return {"heatmap": heatmap}
    
    @staticmethod
    async def get_global_event_counts():
        """
        Counts the occurrences of each event type across all sessions.
        """
        query = """
        MATCH (e:Event)
        RETURN e.event_type AS event_type, COUNT(e) AS count
        """

        async with Neo4jDB.driver.session() as session:
            result = await session.run(query)
            event_counts = {record["event_type"]: record["count"] async for record in result}

        if not event_counts:
            raise HTTPException(status_code=404, detail="No global event data found.")

        return {"event_counts": event_counts}
    
    @staticmethod
    async def get_top_events(limit: int = 5):
        """
        Retrieves the most frequently occurring events.
        """
        query = """
        MATCH (e:Event)
        RETURN e.event_type AS event_type, COUNT(e) AS count
        ORDER BY count DESC LIMIT $limit
        """

        async with Neo4jDB.driver.session() as session:
            result = await session.run(query, limit=limit)
            top_events = [{"event_type": record["event_type"], "count": record["count"]} async for record in result]

        if not top_events:
            raise HTTPException(status_code=404, detail="No event data found.")

        return {"top_events": top_events}
    
    @staticmethod
    async def get_global_funnel(steps: list, start_date: str = None, end_date: str = None):
        """
        Analyzes conversion rates for a funnel across all sessions.
        """
        query = """
        MATCH (s:Session)-[:HAS_EVENT]->(e:Event)
        WHERE e.event_type IN $steps
        """

        if start_date and end_date:
            query += " AND datetime(e.timestamp) >= datetime($start_date) AND datetime(e.timestamp) <= datetime($end_date)"

        query += """
        RETURN e.event_type AS step, COUNT(DISTINCT s.session_id) AS count
        """

        async with Neo4jDB.driver.session() as session:
            params = {"steps": steps}
            if start_date and end_date:
                params.update({"start_date": start_date, "end_date": end_date})

            result = await session.run(query, **params)
            funnel_data = {record["step"]: record["count"] async for record in result}

        if not funnel_data:
            raise HTTPException(status_code=404, detail="No funnel data found.")

        ordered_funnel = {step: funnel_data.get(step, 0) for step in steps}
        return {"funnel": ordered_funnel}
    
    @staticmethod
    async def get_segmented_users(events: list, min_events: int = 1):
        """
        Finds users who triggered specific events at least `min_events` times.
        """
        query = """
        MATCH (u:User)-[:PERFORMED]->(e:Event)
        WHERE e.event_type IN $events
        WITH u, COUNT(e) AS event_count
        WHERE event_count >= $min_events
        RETURN u.user_id AS user_id, event_count
        """

        async with Neo4jDB.driver.session() as session:
            result = await session.run(query, events=events, min_events=min_events)
            segmented_users = [{"user_id": record["user_id"], "event_count": record["event_count"]} async for record in result]

        if not segmented_users:
            raise HTTPException(status_code=404, detail="No users found for this segment.")

        return {"users": segmented_users}
    
    @staticmethod
    async def execute_custom_query(conditions: list):
        """
        Executes a custom query based on user-defined conditions.
        """
        base_query = "MATCH (u:User)-[:PERFORMED]->(e:Event) WHERE "
        filters = []
        params = {}

        for i, condition in enumerate(conditions):
            logic = " AND " if condition.operator == "AND" else " OR "

            if condition.event_filters:
                for event_filter in condition.event_filters:
                    if event_filter.event_type:
                        filters.append(f"e.event_type = $event_type_{i}")
                        params[f"event_type_{i}"] = event_filter.event_type
                    if event_filter.min_occurrences:
                        filters.append(f"(SIZE((u)-[:PERFORMED]->(e)) >= $min_occurrences_{i})")
                        params[f"min_occurrences_{i}"] = event_filter.min_occurrences
                    if event_filter.max_occurrences:
                        filters.append(f"(SIZE((u)-[:PERFORMED]->(e)) <= $max_occurrences_{i})")
                        params[f"max_occurrences_{i}"] = event_filter.max_occurrences
                    if event_filter.start_date and event_filter.end_date:
                        filters.append(f"(datetime(e.timestamp) >= datetime($start_date_{i}) AND datetime(e.timestamp) <= datetime($end_date_{i}))")
                        params[f"start_date_{i}"] = event_filter.start_date
                        params[f"end_date_{i}"] = event_filter.end_date

            if condition.user_filters:
                for user_filter in condition.user_filters:
                    if user_filter.country:
                        filters.append(f"u.country = $country_{i}")
                        params[f"country_{i}"] = user_filter.country
                    if user_filter.device_type:
                        filters.append(f"u.device_type = $device_type_{i}")
                        params[f"device_type_{i}"] = user_filter.device_type
                    if user_filter.min_sessions:
                        filters.append(f"(SIZE((u)-[:HAS_SESSION]->(:Session)) >= $min_sessions_{i})")
                        params[f"min_sessions_{i}"] = user_filter.min_sessions
                    if user_filter.max_sessions:
                        filters.append(f"(SIZE((u)-[:HAS_SESSION]->(:Session)) <= $max_sessions_{i})")
                        params[f"max_sessions_{i}"] = user_filter.max_sessions

        if filters:
            base_query += logic.join(filters)

        base_query += " RETURN u.user_id AS user_id, COUNT(e) AS event_count"

        async with Neo4jDB.driver.session() as session:
            result = await session.run(base_query, **params)
            query_results = [{"user_id": record["user_id"], "event_count": record["event_count"]} async for record in result]

        if not query_results:
            raise HTTPException(status_code=404, detail="No matching users found.")

        return {"users": query_results}
