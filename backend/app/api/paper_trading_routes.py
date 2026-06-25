from fastapi import APIRouter, HTTPException
from typing import Any, Dict, List
from app.portfolio.paper_trading_service import PaperTradingService

router = APIRouter()
service = PaperTradingService()

@router.post("/create", response_model=Dict[str, Any])
def create_paper_portfolio(bundle: Dict[str, Any]):
    """Creates a new paper trading portfolio from a suggested bundle."""
    try:
        portfolio_id = service.create_paper_portfolio(bundle)
        return {"status": "success", "portfolio_id": portfolio_id}
    except Exception as e:
        service.logger.error(f"Error creating paper portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[Dict[str, Any]])
def get_all_paper_portfolios():
    """Retrieves all paper portfolios with real-time P&L."""
    try:
        return service.get_all_paper_portfolios()
    except Exception as e:
        service.logger.error(f"Error fetching paper portfolios: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{portfolio_id}")
def delete_paper_portfolio(portfolio_id: str):
    """Deletes a paper portfolio by ID."""
    success = service.delete_paper_portfolio(portfolio_id)
    if success:
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Portfolio not found")
