import pytest
from app.portfolio.exposure_engine import ExposureEngine
from app.portfolio.kelly_optimizer import KellyOptimizer
from app.portfolio.allocation_engine import AllocationEngine
from app.portfolio.portfolio_analyzer import PortfolioAnalyzer
from app.portfolio.portfolio_orchestrator import PortfolioOrchestrator

def test_exposure_engine():
    engine = ExposureEngine()
    current_portfolio = {
        "cash": 5000.0,
        "total_value": 10000.0,
        "holdings": {
            "TCS": {"sector": "IT", "value": 2000.0}, # 20%
        }
    }
    
    # Candidate in same sector
    candidate_it = {"Ticker": "INFY", "Sector": "IT"}
    max_alloc_it = engine.get_max_allocation(current_portfolio, candidate_it)
    # config max is 0.30. current is 0.20. So 0.10 max left.
    import math
    assert math.isclose(max_alloc_it, 0.10, rel_tol=1e-5)
    
    # Candidate in new sector
    candidate_bank = {"Ticker": "HDFCBANK", "Sector": "BANKING"}
    max_alloc_bank = engine.get_max_allocation(current_portfolio, candidate_bank)
    # config max per stock is 0.15. Since 0% in BANKING, bounded by stock max (0.15)
    assert max_alloc_bank == 0.15

def test_kelly_optimizer():
    optimizer = KellyOptimizer()
    candidate = {"Confidence": 60} # 60% win prob
    
    # kelly = p - (q/b) = 0.6 - (0.4/2) = 0.6 - 0.2 = 0.4
    # half kelly = 0.2
    # bounded to 0.15 config limit
    k = optimizer.calculate_kelly_fraction(candidate)
    
    assert k == 0.15

def test_allocation_engine():
    engine = AllocationEngine()
    
    current_portfolio = {
        "cash": 1000.0,
        "total_value": 10000.0,
        "holdings": {}
    }
    
    candidate = {"Confidence": 60, "Sector": "IT"}
    
    alloc = engine.allocate(current_portfolio, candidate)
    
    # Kelly fraction will cap at 0.15
    # cash available is 1000 (10% of portfolio)
    # Target allocation is 1500 (15%), but capped at 1000 cash.
    assert alloc["final_allocation_cash"] == 1000.0
    assert alloc["final_allocation_pct"] == 0.10

def test_portfolio_analyzer():
    analyzer = PortfolioAnalyzer()
    
    snapshot = {
        "total_value": 100.0,
        "holdings": {
            "A": {"sector": "IT", "value": 50.0},
            "B": {"sector": "BANKING", "value": 50.0}
        }
    }
    
    res = analyzer.analyze(snapshot)
    
    assert res["sector_allocations"]["IT"] == 0.5
    assert res["sector_allocations"]["BANKING"] == 0.5
    # HHI = 0.5^2 + 0.5^2 = 0.25 + 0.25 = 0.50
    assert res["concentration_score"] == 0.50
    assert res["diversification_score"] == 0.50

def test_portfolio_orchestrator():
    orchestrator = PortfolioOrchestrator()
    candidates = [
        {"Ticker": "TCS", "Sector": "IT", "Confidence": 80},
        {"Ticker": "HDFCBANK", "Sector": "BANKING", "Confidence": 40}
    ]
    
    res = orchestrator.filter_and_allocate(candidates)
    
    assert len(res) > 0
    # Higher confidence should be sorted first (assuming MVP optimizer pass-through)
    assert res[0]["Ticker"] == "TCS"
    assert "Portfolio_Fit_Score" in res[0]
    assert "Kelly_Fraction" in res[0]
