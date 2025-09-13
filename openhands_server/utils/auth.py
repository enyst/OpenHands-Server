

from fastapi import HTTPException, Request, status

from openhands_server.config import get_default_config

session_api_key = get_default_config().session_api_key

def validate_session_api_key(request: Request):
    if session_api_key is None:
        return
    if request.headers['X-Session-API-Key'] != session_api_key:
        raise HTTPException(status.HTTP_403_FORBIDDEN)
