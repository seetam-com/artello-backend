from fastapi import FastAPI
from app.core.security import setup_cors
from app.core.database import MongoDB, Neo4jDB
from contextlib import asynccontextmanager
import asyncio
from app.api.v1.events.consumer import process_event

# Import Routes
from app.api.v1.auth.routes import auth_router
from app.api.v1.apps.routes import app_router
from app.api.v1.events.routes import event_router
from app.api.v1.events.analytics import analytics_router
from app.api.v1.graphql.routes import graphql_router

# Define lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handlers for startup and shutdown."""
    # Startup logic
    MongoDB.connect()
    Neo4jDB.connect()
    asyncio.create_task(process_event())
    yield
    # Shutdown logic
    Neo4jDB.close()

# Initialize FastAPI App with lifespan
app = FastAPI(title="Artello API", version="1.0.0", lifespan=lifespan)

# Setup Security Middleware
setup_cors(app)

# Register Routes
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(app_router, prefix="/api/v1/apps")
app.include_router(event_router, prefix="/api/v1/events")
app.include_router(analytics_router, prefix="/api/v1/analytics")
app.include_router(graphql_router, prefix="/graphql")
