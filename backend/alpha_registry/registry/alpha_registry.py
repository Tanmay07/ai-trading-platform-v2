from sqlalchemy.orm import Session
from alpha_registry.registry.alpha_metadata import AlphaFactor, SessionLocal, init_db
from datetime import datetime

class AlphaRegistry:
    """
    CRUD wrapper for the Alpha Factor database.
    """
    def __init__(self):
        init_db()
        
    def register_factor(self, name: str, description: str, category: str, formula: str = ""):
        db = SessionLocal()
        existing = db.query(AlphaFactor).filter(AlphaFactor.name == name).first()
        if not existing:
            factor = AlphaFactor(
                name=name,
                description=description,
                category=category,
                formula=formula,
                status="Experimental"
            )
            db.add(factor)
            db.commit()
            db.refresh(factor)
        db.close()
        
    def get_factor(self, name: str):
        db = SessionLocal()
        factor = db.query(AlphaFactor).filter(AlphaFactor.name == name).first()
        db.close()
        return factor
        
    def get_all_factors(self, status: str = None):
        db = SessionLocal()
        query = db.query(AlphaFactor)
        if status:
            query = query.filter(AlphaFactor.status == status)
        factors = query.all()
        db.close()
        return factors
        
    def update_evaluation(self, name: str, ic: float, rank_ic: float, shap: float = None):
        db = SessionLocal()
        factor = db.query(AlphaFactor).filter(AlphaFactor.name == name).first()
        if factor:
            factor.information_coefficient = ic
            factor.rank_ic = rank_ic
            if shap is not None:
                factor.shap_importance = shap
            factor.last_evaluated = datetime.utcnow()
            db.commit()
        db.close()
        
    def update_status(self, name: str, status: str):
        db = SessionLocal()
        factor = db.query(AlphaFactor).filter(AlphaFactor.name == name).first()
        if factor:
            factor.status = status
            db.commit()
        db.close()
