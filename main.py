from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import date, timedelta
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
    if date_range.start_date > date_range.end_date:
        raise HTTPException(status_code=400, detail="start_date must be before or equal to end_date")

    try:
        # Fetch one extra day before start_date and include end_date
        data = yf.download(
            tickers=DOW_TICKERS,
            start=date_range.start_date - timedelta(days=10),
            end=date_range.end_date + timedelta(days=10),
            group_by='ticker'
        )
        print(data)
        if data.empty:
            raise HTTPException(status_code=404, detail="No data available for the specified date range")

        # Convert start_date and end_date to pandas Timestamp for comparison
        start_date_ts = pd.Timestamp(date_range.start_date)
        end_date_ts = pd.Timestamp(date_range.end_date)
        
        # Initialize the response structure
        response = {
            "returns": {},
            "dates": []
        }
        
        # Calculate daily returns for each stock
        for ticker in DOW_TICKERS:
            if ticker in data:
                # Get closing prices
                close_prices = data[ticker]['Close']
                # Calculate daily returns
                daily_returns = close_prices.pct_change().dropna()
                # Filter returns to the requested date range
                date_index = daily_returns.index
                mask = (date_index >= start_date_ts) & (date_index <= end_date_ts)
                filtered_returns = daily_returns[mask]
                # Convert to list of floats
                response["returns"][ticker] = [float(r) for r in filtered_returns]
        
        # Get the dates from the filtered returns of the first available stock
        first_ticker = next((ticker for ticker in DOW_TICKERS if ticker in data and response["returns"][ticker]), None)
        if first_ticker:
            filtered_dates = data[first_ticker]['Close'].pct_change().dropna().index
            filtered_dates = filtered_dates[(filtered_dates >= start_date_ts) & (filtered_dates <= end_date_ts)]
            response["dates"] = [d.date() for d in filtered_dates]
        else:
            raise HTTPException(status_code=404, detail="No valid returns data for any stock in the date range")
        
        return StockReturns(**response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)