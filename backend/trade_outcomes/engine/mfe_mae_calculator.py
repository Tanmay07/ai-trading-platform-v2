import numpy as np

class MFEMAECalculator:
    """
    Calculates Maximum Favorable Excursion (MFE) and Maximum Adverse Excursion (MAE)
    for simulated trades based on entry price and forward High/Low price action.
    """
    
    @staticmethod
    def calculate_excursions(entry_price: float, forward_highs: np.ndarray, forward_lows: np.ndarray):
        """
        Calculates MFE and MAE for a given entry price and future price action.
        
        Args:
            entry_price (float): The execution price of the trade (usually the Close of signal day)
            forward_highs (np.ndarray): Array of High prices for the holding period
            forward_lows (np.ndarray): Array of Low prices for the holding period
            
        Returns:
            dict: {
                'mfe_pct': float, # Maximum percentage gain achieved
                'mae_pct': float, # Maximum percentage loss suffered
                'highest_high': float,
                'lowest_low': float
            }
        """
        if len(forward_highs) == 0 or len(forward_lows) == 0:
            return {
                'mfe_pct': 0.0,
                'mae_pct': 0.0,
                'highest_high': entry_price,
                'lowest_low': entry_price
            }
            
        highest_high = np.max(forward_highs)
        lowest_low = np.min(forward_lows)
        
        mfe_pct = ((highest_high - entry_price) / entry_price) * 100.0
        mae_pct = ((lowest_low - entry_price) / entry_price) * 100.0
        
        return {
            'mfe_pct': mfe_pct,
            'mae_pct': mae_pct,
            'highest_high': highest_high,
            'lowest_low': lowest_low
        }
