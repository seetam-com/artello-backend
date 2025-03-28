from fastapi import Security, HTTPException, Request
from fastapi.security import APIKeyHeader
from app.core.database import MongoDB

app_key_header = APIKeyHeader(name="X-APP-KEY", auto_error=False)

async def verify_sdk_key(request: Request, app_key: str = Security(app_key_header)):
    """
    Verifies the SDK key and validates the domain of the request.
    """
    mongo_db = MongoDB.get_db()
    app = await mongo_db.apps.find_one({"app_key": app_key})

    if not app:
        raise HTTPException(status_code=401, detail="Invalid app key")

    # Extract domain from request headers
    origin = request.headers.get("origin") or request.headers.get("referer")
    if not origin:
        raise HTTPException(status_code=400, detail="Missing origin or referer header")

    # Validate domain
    registered_domain = app.get("domain")
    if not registered_domain or registered_domain not in origin:
        raise HTTPException(status_code=403, detail="Domain not authorized for this app key")

    return app["app_id"]
