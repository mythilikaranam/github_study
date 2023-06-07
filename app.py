import datetime as dt
from typing import Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()

# Mocked database and data
class Database:
    def __init__(self):
        self.trades = []
    
    def add_trade(self, trade):
        self.trades.append(trade)
    
    def get_trade_by_id(self, trade_id):
        for trade in self.trades:
            if trade.trade_id == trade_id:
                return trade
        return None
    
    def search_trades(self, search_text):
        results = []
        for trade in self.trades:
            if (
                search_text in trade.counterparty or
                search_text in trade.instrument_id or
                search_text in trade.instrument_name or
                search_text in trade.trader
            ):
                results.append(trade)
        return results
    
    def filter_trades(
        self,
        asset_class: Optional[str] = None,
        end: Optional[dt.datetime] = None,
        max_price: Optional[float] = None,
        min_price: Optional[float] = None,
        start: Optional[dt.datetime] = None,
        trade_type: Optional[str] = None,
    ):
        results = []
        for trade in self.trades:
            if (
                (asset_class is None or trade.asset_class == asset_class) and
                (end is None or trade.trade_date_time <= end) and
                (max_price is None or trade.trade_details.price <= max_price) and
                (min_price is None or trade.trade_details.price >= min_price) and
                (start is None or trade.trade_date_time >= start) and
                (trade_type is None or trade.trade_details.buySellIndicator == trade_type)
            ):
                results.append(trade)
        return results

db = Database()


# Schema model
class TradeDetails(BaseModel):
    buySellIndicator: str = Field(description="A value of BUY for buys, SELL for sells.")
    price: float = Field(description="The price of the Trade.")
    quantity: int = Field(description="The amount of units traded.")


class Trade(BaseModel):
    asset_class: Optional[str] = Field(alias="assetClass", default=None, description="The asset class of the instrument traded. E.g. Bond, Equity, FX...etc")
    counterparty: Optional[str] = Field(default=None, description="The counterparty the trade was executed with. May not always be available")
    instrument_id: str = Field(alias="instrumentId", description="The ISIN/ID of the instrument traded. E.g. TSLA, AAPL, AMZN...etc")
    instrument_name: str = Field(alias="instrumentName", description="The name of the instrument traded.")
    trade_date_time: dt.datetime = Field(alias="tradeDateTime", description="The date-time the Trade was executed")
    trade_details: TradeDetails = Field(alias="tradeDetails", description="The details of the trade, i.e. price, quantity")
    trade_id: str = Field(alias="tradeId", default=None, description="The unique ID of the trade")
    trader: str = Field(description="The name of the Trader")


# Endpoints
@app.post("/trades")
def create_trade(trade: Trade):
    db.add_trade(trade)
    return {"message": "Trade created successfully"}


@app.get("/trades")
def get_trades(
    search: Optional[str] = Query(None, description="Search text for counterparty, instrumentId
