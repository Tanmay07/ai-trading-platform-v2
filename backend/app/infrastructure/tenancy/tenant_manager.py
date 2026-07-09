from typing import Dict, Any
from contextvars import ContextVar

# Current tenant context
_tenant_id_ctx_var: ContextVar[str] = ContextVar("tenant_id", default="default_tenant")

class TenantManager:
    @staticmethod
    def set_tenant(tenant_id: str):
        _tenant_id_ctx_var.set(tenant_id)
        
    @staticmethod
    def get_tenant() -> str:
        return _tenant_id_ctx_var.get()
        
    def isolate_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attaches the current tenant_id to the payload before DB insertion.
        """
        payload["tenant_id"] = self.get_tenant()
        return payload
