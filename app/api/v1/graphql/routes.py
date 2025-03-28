import strawberry
from strawberry.fastapi import GraphQLRouter
from app.api.v1.auth.dependencies import verify_api_key
from app.api.v1.graphql.schemas import Query

# Create GraphQL Schema
schema = strawberry.Schema(query=Query)

# Secure GraphQL API with API Key Authentication
async def get_context(api_key: str = verify_api_key):
    return {"app": api_key}

graphql_router = GraphQLRouter(schema, context_getter=get_context)
