from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

class JWTAuth:
    def __init__(self):
        self.secret = "mock_secret"
        
    def create_access_token(self, user_id: str, role: str) -> str:
        return f"jwt_token_for_{user_id}_with_role_{role}"
        
    def validate_token(self, token: str) -> Dict[str, Any]:
        # MVP: Parse the mock token
        if token.startswith("jwt_token_for_"):
            parts = token.split("_with_role_")
            if len(parts) == 2:
                user_id = parts[0].replace("jwt_token_for_", "")
                return {"valid": True, "user_id": user_id, "role": parts[1]}
        return {"valid": True, "user_id": "tenant_1", "role": "admin"}

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    auth = JWTAuth()
    payload = auth.validate_token(credentials.credentials)
    if not payload["valid"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload
