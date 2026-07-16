class RoadmapGenerator:
    @staticmethod
    def generate_roadmap(feature_stats, sector_stats, risk_stats, regime_stats):
        recommendations = {
            "Features_To_Remove": feature_stats.get('Features_To_Remove', []),
            "Sectors_To_Prioritize": [s['Sector'] for s in sector_stats.get('Top_Performing_Sectors', [])[:3]],
            "Sectors_To_Avoid": [s['Sector'] for s in sector_stats.get('Bottom_Performing_Sectors', [])[-3:]],
            "Recommended_Holding_Period": "See Holding Period Analysis",
            "Optimal_Profit_Target": risk_stats.get('Recommendations', {}).get('Optimal_Profit_Target'),
            "Optimal_Stop_Loss": risk_stats.get('Recommendations', {}).get('Optimal_Stop_Loss'),
            "Feature_Expansion_Ideas": [
                {
                    "Priority": 1,
                    "Idea": "Relative Strength against Sector Index",
                    "Rationale": "Sector performance deeply impacts trade quality.",
                    "Expected_Impact": "High"
                },
                {
                    "Priority": 2,
                    "Idea": "Regime-Aware Volatility (VIX ratio)",
                    "Rationale": "Market regime heavily dictates success rates.",
                    "Expected_Impact": "High"
                },
                {
                    "Priority": 3,
                    "Idea": "Multi-Timeframe Trend Alignment",
                    "Rationale": "Trend strength shows strong Spearman correlation.",
                    "Expected_Impact": "Medium"
                }
            ]
        }
        return recommendations
