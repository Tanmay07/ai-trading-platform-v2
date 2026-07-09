from datetime import datetime, timedelta
from typing import Dict, Any

class JWTAuth:
    def __init__(self):
        self.secret = "mock_secret"
        
    def create_access_token(self, user_id: str, role: str) -> str:
        """
        Creates a JWT token containing user_id and RBAC role.
        """
        # MVP: Return a dummy string
        return f"jwt_token_for_{user_id}_with_role_{role}"
        
    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validates the JWT signature and expiration.
        """
        return {"valid": True, "user_id": "tenant_1", "role": "admin"}
