import os

from langgraph_sdk import Auth

auth = Auth()


@auth.authenticate
async def authenticate(headers: dict) -> Auth.types.MinimalUserDict:
    expected = os.environ.get("APP_PASSCODE")
    if not expected:
        raise Auth.exceptions.HTTPException(
            status_code=500, detail="APP_PASSCODE not configured"
        )
    provided = headers.get(b"x-app-passcode", b"").decode()
    if provided != expected:
        raise Auth.exceptions.HTTPException(status_code=401, detail="Bad passcode")
    email = headers.get(b"x-user-email", b"anonymous").decode() or "anonymous"
    return {"identity": email, "permissions": []}
