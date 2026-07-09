import pytest
from app.hfos.compliance_engine import ComplianceEngine
from app.hfos.investment_committee import InvestmentCommittee
from app.hfos.hfos_orchestrator import HFOSOrchestrator

def test_compliance():
    engine = ComplianceEngine()
    
    # Should pass
    assert engine.check_pre_trade({"symbol": "RELIANCE"}) is True
    
    # Should block restricted
    assert engine.check_pre_trade({"symbol": "ITC"}) is False
    
def test_committee():
    committee = InvestmentCommittee()
    res = committee.review_recommendation({"symbol": "TCS"})
    
    # Based on the mocked AI votes, there are 4 buy votes, which meets the threshold
    assert res["status"] == "APPROVED"
    assert res["votes_for"] >= 4

def test_hfos_orchestrator():
    orchestrator = HFOSOrchestrator()
    
    # Test blocked trade
    res = orchestrator.process_recommendation({"symbol": "ITC"})
    assert res["status"] == "BLOCKED"
    
    # Test approved trade
    res2 = orchestrator.process_recommendation({"symbol": "INFY"})
    assert res2["status"] == "EXECUTED"
    assert "allocated_capital_pct" in res2
