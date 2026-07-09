import pytest
from unittest.mock import MagicMock
from market_data.providers.provider_router import ProviderRouter
from market_data.cache.cache_manager import CacheManager
from market_data.orchestrator.priority_engine import PriorityEngine, PriorityLevel
from market_data.orchestrator.event_trigger_engine import EventTriggerEngine
from market_data.orchestrator.market_data_orchestrator import MarketDataOrchestrator
from data_platform.core.config_manager import ConfigManager

def test_priority_engine():
    config = ConfigManager()
    engine = PriorityEngine(config)
    
    # Default is Dormant
    assert engine.get_priority("RELIANCE") == PriorityLevel.DORMANT
    
    # High volume should trigger CRITICAL
    metrics = {"relative_volume": 4.0, "gap_pct": 0.01}
    priority = engine.evaluate_priority("RELIANCE", metrics)
    assert priority == PriorityLevel.CRITICAL
    assert engine.get_priority("RELIANCE") == PriorityLevel.CRITICAL

def test_event_trigger_engine():
    config = ConfigManager()
    priority_engine = PriorityEngine(config)
    event_engine = EventTriggerEngine(priority_engine, config)
    
    # Process tick that should trigger volume explosion
    prev_metrics = {"Vol_SMA_20": 1000, "Close": 100}
    
    event_engine.process_tick("INFY", 102, 5000, prev_metrics)
    
    assert len(event_engine.event_log) > 0
    assert event_engine.event_log[0]["event"] == "VOLUME_EXPLOSION"
    assert priority_engine.get_priority("INFY") == PriorityLevel.CRITICAL

def test_cache_fallback():
    # If redis fails to connect, it should fallback to memory gracefully
    config = ConfigManager()
    cache_mgr = CacheManager(config)
    
    # Should work (either in real redis or in-memory fallback)
    cache_mgr.set_price("TCS", {"price": 3000})
    data = cache_mgr.get_price("TCS")
    
    assert data is not None
    assert data["price"] == 3000
    assert cache_mgr.hits == 1

def test_provider_router():
    config = ConfigManager()
    router = ProviderRouter(config)
    
    # Mocking the providers to test routing logic
    mock_yahoo = MagicMock()
    mock_yahoo.get_provider_name.return_value = "yahoo"
    mock_yahoo.fetch_current_price.return_value = {"status": "error"}
    
    mock_jugaad = MagicMock()
    mock_jugaad.get_provider_name.return_value = "jugaad"
    mock_jugaad.fetch_current_price.return_value = {"status": "success", "price": 100}
    
    router.providers["yahoo"] = mock_yahoo
    router.providers["jugaad"] = mock_jugaad
    
    # It should try yahoo, fail, try jugaad, succeed
    result = router.get_price("TEST")
    
    assert result["status"] == "success"
    assert result["price"] == 100
    mock_yahoo.fetch_current_price.assert_called_once()
    mock_jugaad.fetch_current_price.assert_called_once()
