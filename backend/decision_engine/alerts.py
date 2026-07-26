from sqlalchemy.orm import Session
from decision_engine.database import AlertRecord
from decision_engine.models import RecommendationObject
import logging

logger = logging.getLogger(__name__)

class AlertEngine:
    @staticmethod
    def check_and_generate_alerts(db: Session, user_id: str, current_price: float, rec: RecommendationObject):
        """
        Checks if the current price breaches targets or stops and generates DB alerts.
        """
        try:
            alert_type = None
            message = None
            
            if current_price >= rec.target_price_1 and rec.target_price_1 > 0:
                alert_type = "TARGET_REACHED"
                message = f"{rec.symbol} has reached Target 1 ({rec.target_price_1}). Consider booking partial profits."
                
            elif current_price <= rec.stop_loss and rec.stop_loss > 0:
                alert_type = "STOP_LOSS_BREACHED"
                message = f"{rec.symbol} has breached Stop Loss ({rec.stop_loss}). Risk containment activated."
                
            if alert_type:
                # Check if we already alerted today (naive check, usually requires timestamp filtering)
                # For Phase P3 we just insert
                alert = AlertRecord(
                    user_id=user_id,
                    symbol=rec.symbol,
                    alert_type=alert_type,
                    message=message
                )
                db.add(alert)
                db.commit()
                logger.info(f"Generated Alert: {message}")
                
        except Exception as e:
            logger.error(f"Failed to generate alert for {rec.symbol}: {str(e)}")
