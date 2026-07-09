import pytest
from app.infrastructure.auth.jwt_auth import JWTAuth
from app.infrastructure.tenancy.tenant_manager import TenantManager
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.infrastructure_manager import InfrastructureManager

def test_jwt_auth():
    auth = JWTAuth()
    token = auth.create_access_token("user1", "admin")
    assert "user1" in token
    assert "admin" in token
    
    val = auth.validate_token(token)
    assert val["valid"] is True

def test_tenancy():
    manager = TenantManager()
    manager.set_tenant("tenant_99")
    
    assert manager.get_tenant() == "tenant_99"
    payload = manager.isolate_data({"stock": "AAPL"})
    assert payload["tenant_id"] == "tenant_99"
    
def test_cache():
    cache = RedisCache()
    cache.set("price_aapl", {"price": 150.0})
    
    val = cache.get("price_aapl")
    assert val["price"] == 150.0
    
    cache.invalidate("price_aapl")
    assert cache.get("price_aapl") is None

def test_infrastructure_manager():
    manager = InfrastructureManager()
    health = manager.check_health()
    assert health["status"] == "HEALTHY"
    assert health["database"] == "UP"
