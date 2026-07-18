import logging
from typing import List, Dict

logger = logging.getLogger("AlertsEngine")

class AlertsEngine:
    def __init__(self):
        pass
        
    def generate_alerts(self, risk_metrics: Dict, health: Dict, recommendations: List[Dict]) -> List[Dict]:
        """
        Scans portfolio state and returns active alerts.
        """
        alerts = []
        
        if health.get('health_score', 100) < 70:
            alerts.append({
                "severity": "high",
                "message": f"Portfolio Health dropped to {health['health_score']}. Review diversification."
            })
            
        if risk_metrics.get('portfolio_volatility', 0) > 0.35:
            alerts.append({
                "severity": "medium",
                "message": "Portfolio Volatility is elevated (>35%)."
            })
            
        buys = [r for r in recommendations if r.get('recommendation') == 'BUY' and r.get('confidence', 0) > 0.80]
        for b in buys:
            alerts.append({
                "severity": "info",
                "message": f"High Conviction BUY Opportunity: {b['symbol']} ({b['confidence']*100:.1f}%)"
            })
            
        return alerts
