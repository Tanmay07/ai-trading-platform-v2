class AlphaFactory:
    def generate_candidate_factors(self) -> list:
        """
        Combines mathematical transformations of basic features into candidate alphas.
        """
        return [
            {"formula": "RSI_14 / ATR_20", "description": "Momentum over Volatility"},
            {"formula": "close / sma_200", "description": "Long-term trend"}
        ]
