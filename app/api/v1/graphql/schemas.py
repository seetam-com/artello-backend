import strawberry
from datetime import datetime
from typing import Optional, List
from strawberry.scalars import JSON

def parse_timestamp(timestamp: str) -> datetime:
    """
    Converts string timestamp to datetime object.
    """
    return datetime.fromisoformat(timestamp) if isinstance(timestamp, str) else timestamp

@strawberry.type
class Event:
    event_id: str
    event_type: str
    timestamp: datetime
    payload: JSON
    next_event: Optional[str] = None  # Links to the next event in sequence

    @strawberry.field
    def formatted_timestamp(self) -> str:
        """
        Returns timestamp in ISO format for GraphQL responses.
        """
        return self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else str(self.timestamp)

@strawberry.type
class SessionAnalytics:
    session_id: str
    event_counts: JSON

@strawberry.type
class ConversionFunnel:
    session_id: str
    funnel: JSON

@strawberry.type
class RetentionRate:
    days: int
    active_sessions: int

@strawberry.type
class HeatmapData:
    heatmap: JSON

@strawberry.type
class GlobalAnalytics:
    event_counts: JSON

@strawberry.type
class TopEvents:
    top_events: JSON

@strawberry.type
class GlobalFunnel:
    funnel: JSON

@strawberry.type
class SegmentedUsers:
    users: JSON

@strawberry.input
class EventFilter:
    """
    Defines filters for querying events dynamically.
    """
    event_type: Optional[str] = None
    min_occurrences: Optional[int] = None
    max_occurrences: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

@strawberry.input
class UserFilter:
    """
    Defines filters for querying users dynamically.
    """
    country: Optional[str] = None
    device_type: Optional[str] = None
    min_sessions: Optional[int] = None
    max_sessions: Optional[int] = None

@strawberry.input
class QueryCondition:
    """
    Defines conditions for custom queries (AND / OR logic).
    """
    operator: str  # "AND" or "OR"
    event_filters: Optional[List[EventFilter]] = None
    user_filters: Optional[List[UserFilter]] = None

@strawberry.type
class QueryResults:
    """
    Returns the results of custom analytics queries.
    """
    results: JSON

@strawberry.type
class Query:
    """
    Defines GraphQL queries for event analytics.
    """
    @strawberry.field
    async def event_flow(self, session_id: str) -> List[Event]:
        """
        Fetches the ordered sequence of events in a session.
        """
        from app.api.v1.events.queries import EventQueries
        result = await EventQueries.get_event_flow(session_id)
        return [Event(
            event_id=e["event_id"],
            event_type=e["event_type"],
            timestamp=parse_timestamp(e["timestamp"]),
            payload=e["payload"],
            next_event=e["next_event"]
        ) for e in result["events"]]

    @strawberry.field
    async def latest_event(self, session_id: str) -> Event:
        """
        Fetches the most recent event in a session.
        """
        from app.api.v1.events.queries import EventQueries
        result = await EventQueries.get_latest_event(session_id)
        return Event(
            event_id=result["event_id"],
            event_type=result["event_type"],
            timestamp=parse_timestamp(result["timestamp"]),
            payload=result["payload"]
        )

    @strawberry.field
    async def event_counts(self, session_id: str) -> SessionAnalytics:
        """
        Fetches the event occurrence count in a session.
        """
        from app.api.v1.events.queries import EventQueries
        result = await EventQueries.get_event_counts(session_id)
        return SessionAnalytics(session_id=result["session_id"], event_counts=result["event_counts"])
    
    @strawberry.field
    async def conversion_funnel(self, session_id: str, steps: List[str]) -> ConversionFunnel:
        """
        Fetches conversion funnel data.
        """
        from app.api.v1.events.queries import EventQueries
        result = await EventQueries.get_conversion_funnel(session_id, steps)
        return ConversionFunnel(**result)

    @strawberry.field
    async def retention_rate(self, days: int) -> RetentionRate:
        """
        Fetches user retention over a specified number of days.
        """
        from app.api.v1.events.queries import EventQueries
        result = await EventQueries.get_retention_rate(days)
        return RetentionRate(**result)

    @strawberry.field
    async def session_heatmap(self) -> HeatmapData:
        """
        Fetches session heatmap data.
        """
        from app.api.v1.events.queries import EventQueries
        result = await EventQueries.get_session_heatmap()
        return HeatmapData(**result)
    
    @strawberry.field
    async def global_event_counts(self) -> GlobalAnalytics:
        """
        Fetches event frequency across all sessions.
        """
        from app.api.v1.events.queries import EventQueries
        result = await EventQueries.get_global_event_counts()
        return GlobalAnalytics(**result)

    @strawberry.field
    async def top_events(self, limit: int = 5) -> TopEvents:
        """
        Fetches the most frequent event types.
        """
        from app.api.v1.events.queries import EventQueries
        result = await EventQueries.get_top_events(limit)
        return TopEvents(**result)

    @strawberry.field
    async def global_funnel(self, steps: List[str], start_date: str = None, end_date: str = None) -> GlobalFunnel:
        """
        Fetches funnel data across all sessions.
        """
        from app.api.v1.events.queries import EventQueries
        result = await EventQueries.get_global_funnel(steps, start_date, end_date)
        return GlobalFunnel(**result)

    @strawberry.field
    async def segmented_users(self, events: List[str], min_events: int = 1) -> SegmentedUsers:
        """
        Fetches users based on event frequency.
        """
        from app.api.v1.events.queries import EventQueries
        result = await EventQueries.get_segmented_users(events, min_events)
        return SegmentedUsers(**result)
    
    @strawberry.field
    async def custom_query(self, conditions: List[QueryCondition]) -> QueryResults:
        """
        Executes a custom analytics query with dynamic conditions.
        """
        from app.api.v1.events.queries import EventQueries
        result = await EventQueries.execute_custom_query(conditions)
        return QueryResults(results=result)
