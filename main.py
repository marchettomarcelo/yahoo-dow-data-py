from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import  List, Dict
from datetime import date
import yfinance as yf
import pandas as pd

app = FastAPI(
    title="DowData API",
    description="A FastAPI boilerplate for DowData",
    version="0.1.0"
)

# Dow Jones Industrial Average components
DOW_TICKERS = [
    "AAPL", "AMGN", "AXP", "BA", "CAT", "CRM", "CSCO", "CVX", "DIS", "DOW",
    "GS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM",
    "MRK", "MSFT", "NKE", "PG", "TRV", "UNH", "V", "VZ", "WBA", "WMT"
]

class DateRange(BaseModel):
    start_date: date
    end_date: date

class StockReturns(BaseModel):
    returns: Dict[str, List[float]]
    dates: List[date]

@app.post("/dow/daily-returns")
async def get_dow_daily_returns(date_range: DateRange) -> StockReturns:
    try:
        # Download data for all Dow stocks
        data = yf.download(
            tickers=DOW_TICKERS,
            start=date_range.start_date,
            end=date_range.end_date,
            group_by='ticker'
        )
        
        # Initialize the response structure
        response = {
            "returns": {},
            "dates": []
        }
        
        # Get the dates from the first available stock
        first_ticker = next((ticker for ticker in DOW_TICKERS if ticker in data), None)
        if first_ticker:
            dates = data[first_ticker].index
            response["dates"] = [d.date() for d in dates]
        
        # Calculate daily returns for each stock
        for ticker in DOW_TICKERS:
            if ticker in data:
                # Get closing prices
                close_prices = data[ticker]['Close']
                # Calculate daily returns
                daily_returns = close_prices.pct_change().dropna()
                # Convert to list of floats
                response["returns"][ticker] = [float(r) for r in daily_returns]
        
        return StockReturns(**response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
