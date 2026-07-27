from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from portfolio_manager.database import get_db
from portfolio_manager.schemas import (
    PortfolioCreate, PortfolioResponse,
    TransactionCreate, TransactionResponse,
    HoldingResponse, PortfolioSummaryResponse
)
from portfolio_manager.portfolio_service import PortfolioService
from app.infrastructure.auth.jwt_auth import get_current_user
from market_data.service import MarketDataService
from market_data.providers.jugaad_provider import JugaadProvider
from market_data.providers.yahoo_provider import YahooProvider
from portfolio_manager.importer import CSVImporter
from portfolio_manager.exporter import CSVExporter

router = APIRouter()

def get_portfolio_service(db: Session = Depends(get_db)):
    providers = [JugaadProvider(), YahooProvider()]
    mds = MarketDataService(providers=providers)
    return PortfolioService(db, mds)

@router.post("/", response_model=PortfolioResponse)
def create_portfolio(
    data: PortfolioCreate,
    user: dict = Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service)
):
    return service.create_portfolio(user["user_id"], data)

@router.get("/", response_model=List[PortfolioResponse])
def list_portfolios(
    user: dict = Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service)
):
    return service.list_portfolios(user["user_id"])

@router.get("/{id}/holdings", response_model=List[HoldingResponse])
def get_holdings(
    id: int,
    user: dict = Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service)
):
    return service.get_holdings(id, user["user_id"])

@router.post("/{id}/transaction", response_model=TransactionResponse)
def add_transaction(
    id: int,
    data: TransactionCreate,
    user: dict = Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service)
):
    return service.add_transaction(id, user["user_id"], data)

@router.get("/{id}/summary", response_model=PortfolioSummaryResponse)
def get_summary(
    id: int,
    user: dict = Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service)
):
    return service.get_summary(id, user["user_id"])

@router.post("/{id}/import")
async def import_transactions_csv(
    id: int,
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service)
):
    content = await file.read()
    transactions = CSVImporter.parse_transactions(content.decode("utf-8"))
    for t in transactions:
        service.add_transaction(id, user["user_id"], t)
    return {"message": f"Imported {len(transactions)} transactions."}

@router.get("/{id}/export/csv")
def export_holdings_csv(
    id: int,
    user: dict = Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service)
):
    from fastapi.responses import PlainTextResponse
    holdings = service.get_holdings(id, user["user_id"])
    csv_str = CSVExporter.export_holdings(holdings)
    return PlainTextResponse(content=csv_str, media_type="text/csv")
