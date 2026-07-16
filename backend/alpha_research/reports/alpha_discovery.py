class AlphaDiscovery:
    @staticmethod
    def discover_alpha(indicator_stats, correlation_stats, feature_stats, config):
        """
        Synthesizes the other reports to find "discoveries" - statistically significant Outperformance.
        """
        discoveries = []
        
        # Look for high correlation features
        for f in correlation_stats.get('Correlations', []):
            if abs(f['Spearman_Correlation']) > 0.15:
                direction = "Positive" if f['Spearman_Correlation'] > 0 else "Negative"
                discoveries.append({
                    "Insight": f"Strong {direction} relationship between {f['Feature']} and Trade Quality.",
                    "Evidence": f"Spearman Corr: {f['Spearman_Correlation']}",
                    "Confidence": "High"
                })
                
        # Look for Indicator Outperformance
        for ind, bins in indicator_stats.items():
            for b in bins:
                if b['Average_Quality'] > 50 and b['Count'] >= config.get('significance_threshold', {}).get('min_trades', 500):
                    discoveries.append({
                        "Insight": f"{ind} in range {b['Range']} historically generates extremely high-quality swing trades.",
                        "Evidence": f"Average Quality: {b['Average_Quality']} across {b['Count']} trades.",
                        "Confidence": "Very High" if b['Count'] > 2000 else "Medium"
                    })
                    
        return sorted(discoveries, key=lambda x: 1 if x["Confidence"] == "High" else 2)[:20]
