import logging
from typing import Dict, Any

logger = logging.getLogger("DailyBrief")

class DailyBriefGenerator:
    """
    Auto-generates the textual daily investment brief.
    """
    def __init__(self):
        pass
        
    def generate_brief(self, market_data: Dict, portfolio_data: Dict, recs_data: list) -> str:
        """
        Synthesizes a cohesive executive summary.
        """
        # Market
        m_txt = market_data.get('summary_text', '')
        
        # Portfolio
        val = portfolio_data.get('total_value', 0)
        cash = portfolio_data.get('cash_balance', 0)
        cash_pct = (cash / val * 100) if val > 0 else 0
        p_txt = f"The portfolio value stands at ${val:,.2f} with {cash_pct:.1f}% held in cash."
        
        # Recs
        buys = sum(1 for r in recs_data if r.get('recommendation') == 'BUY')
        r_txt = f"The AI engine has identified {buys} new high-conviction BUY candidates."
        if buys > 0:
            top_buy = next((r for r in recs_data if r.get('recommendation') == 'BUY'), None)
            if top_buy:
                r_txt += f" The top opportunity is {top_buy['symbol']} with a target weight of {top_buy.get('target_weight',0)*100:.1f}%."
                
        # Action
        a_txt = "Action Item: Review the new buy candidates in the Decision Workspace and confirm any rebalancing required."
        
        brief = f"### Daily Investment Brief\\n\\n**Market Update**\\n{m_txt}\\n\\n**Portfolio Update**\\n{p_txt}\\n\\n**AI Intelligence**\\n{r_txt}\\n\\n**Recommendation**\\n{a_txt}"
        return brief
