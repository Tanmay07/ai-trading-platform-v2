import logging
from typing import Dict, Any, List

from market_data.providers.base_provider import BaseIntradayProvider
from market_data.providers.yahoo_provider import YahooIntradayProvider
from market_data.providers.jugaad_provider import JugaadProvider
from data_platform.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class ProviderRouter:
    """
    Routes requests to the preferred provider and handles failovers.
    """
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager.get_config("market_data")
        
        self.providers: Dict[str, BaseIntradayProvider] = {
            "yahoo": YahooIntradayProvider(),
            "jugaad": JugaadProvider(),
            # "nse": NSEProvider() # Placeholder for official NSE API if needed
        }
        
    def _get_provider_chain(self, data_type: str = "intraday_price") -> List[BaseIntradayProvider]:
        routing = self.config.get("provider_routing", {})
        chain_names = routing.get(data_type, ["yahoo"])
        
        chain = []
        for name in chain_names:
            if name in self.providers:
                chain.append(self.providers[name])
                
        if not chain:
            # Fallback
            chain = [self.providers["yahoo"]]
            
        return chain

    def get_price(self, symbol: str) -> Dict[str, Any]:
        chain = self._get_provider_chain("intraday_price")
        
        for provider in chain:
            logger.debug(f"Attempting to fetch {symbol} price using {provider.get_provider_name()}")
            result = provider.fetch_current_price(symbol)
            if result.get("status") == "success":
                return result
            logger.warning(f"Provider {provider.get_provider_name()} failed for {symbol}: {result.get('error')}")
            
        logger.error(f"All providers failed to fetch price for {symbol}")
        return {"symbol": symbol, "status": "error", "error": "All providers exhausted"}

    def get_batch_prices(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        chain = self._get_provider_chain("intraday_price")
        final_results = {}
        pending_symbols = symbols.copy()
        
        for provider in chain:
            if not pending_symbols:
                break
                
            logger.debug(f"Attempting batch fetch for {len(pending_symbols)} symbols using {provider.get_provider_name()}")
            results = provider.fetch_batch_prices(pending_symbols)
            
            for sym, res in results.items():
                if res.get("status") == "success":
                    final_results[sym] = res
                    pending_symbols.remove(sym)
                    
        # Log failures for any remaining
        for sym in pending_symbols:
            logger.error(f"All providers failed to fetch price for {sym}")
            final_results[sym] = {"symbol": sym, "status": "error", "error": "All providers exhausted"}
            
        return final_results
