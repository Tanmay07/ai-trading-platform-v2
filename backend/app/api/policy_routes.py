from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from policy_engine.database import get_db
from policy_engine.models import Policy, PolicyVersion, DecisionAuditLog
from policy_engine.schemas import PolicyCreate, PolicyResponse, PolicyVersionCreate, PolicyVersionResponse
from app.infrastructure.auth.jwt_auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[PolicyResponse])
def get_policies(db: Session = Depends(get_db)):
    """Get all policies"""
    return db.query(Policy).all()

@router.post("/", response_model=PolicyResponse)
def create_policy(policy_in: PolicyCreate, db: Session = Depends(get_db)):
    """Create a new policy and its initial v1.0 version"""
    # Create Base Policy
    policy = Policy(
        name=policy_in.name,
        description=policy_in.description,
        investment_style=policy_in.investment_style,
        benchmark=policy_in.benchmark
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    
    # Create v1
    v = policy_in.initial_version
    version = PolicyVersion(
        policy_id=policy.id,
        version_number=1,
        status="ACTIVE",
        weights=v.weights.model_dump(),
        thresholds=v.thresholds.model_dump(),
        target_logic=v.target_logic.model_dump(),
        stop_loss_logic=v.stop_loss_logic.model_dump(),
        sizing_rules=v.sizing_rules,
        review_rules=v.review_rules,
        market_regime_rules=v.market_regime_rules
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    
    # Set active
    policy.active_version_id = version.id
    db.commit()
    db.refresh(policy)
    
    return policy

@router.post("/{policy_id}/clone", response_model=PolicyResponse)
def clone_policy(policy_id: int, new_name: str, db: Session = Depends(get_db)):
    """Clones an existing policy into a new one"""
    orig_policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not orig_policy:
        raise HTTPException(status_code=404, detail="Policy not found")
        
    orig_v = db.query(PolicyVersion).filter(PolicyVersion.id == orig_policy.active_version_id).first()
    
    new_policy = Policy(
        name=new_name,
        description=orig_policy.description,
        investment_style=orig_policy.investment_style,
        benchmark=orig_policy.benchmark
    )
    db.add(new_policy)
    db.commit()
    db.refresh(new_policy)
    
    new_v = PolicyVersion(
        policy_id=new_policy.id,
        version_number=1,
        status="ACTIVE",
        weights=orig_v.weights,
        thresholds=orig_v.thresholds,
        target_logic=orig_v.target_logic,
        stop_loss_logic=orig_v.stop_loss_logic,
        sizing_rules=orig_v.sizing_rules,
        review_rules=orig_v.review_rules,
        market_regime_rules=orig_v.market_regime_rules
    )
    db.add(new_v)
    db.commit()
    db.refresh(new_v)
    
    new_policy.active_version_id = new_v.id
    db.commit()
    db.refresh(new_policy)
    
    return new_policy

@router.get("/audit", response_model=List[dict])
def get_audit_trail(db: Session = Depends(get_db)):
    """Fetches the Decision Audit Trail"""
    logs = db.query(DecisionAuditLog).order_by(DecisionAuditLog.timestamp.desc()).limit(100).all()
    
    return [
        {
            "id": log.id,
            "portfolio_id": log.portfolio_id,
            "symbol": log.symbol,
            "policy_version_id": log.policy_version_id,
            "decision": log.decision,
            "confidence": log.confidence,
            "explanation": log.explanation,
            "timestamp": log.timestamp
        }
        for log in logs
    ]

@router.get("/health/policy-engine")
def health_check():
    return {"status": "ok", "message": "Decision Policy Engine operational."}
