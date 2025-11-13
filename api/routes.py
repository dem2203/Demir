# api/routes.py

from fastapi import FastAPI, HTTPException
from typing import Dict
import asyncio

app = FastAPI(title="Demir AI Bot API", version="1.0.0")

@app.get("/health")
async def health_check():
    """System health check"""
    return {"status": "healthy"}

@app.get("/price/{symbol}")
async def get_price(symbol: str):
    """Get REAL price from orchestrator"""
    orchestrator = MultiAPIOrchestrator()
    price = await orchestrator.get_price(symbol, futures=False)
    return price

@app.get("/signal/{symbol}")
async def get_signal(symbol: str):
    """Get AI signal for symbol"""
    # Run all layers
    # Return consolidated signal
    pass

@app.get("/trades/history")
async def get_trade_history(limit: int = 100):
    """Get recent trades from database"""
    db = PersistenceLayer()
    trades = await db.get_recent_trades(limit)
    return trades

@app.post("/telegram/test")
async def test_telegram():
    """Test Telegram integration"""
    manager = AdvancedTelegramManager(
        os.getenv('TELEGRAM_TOKEN'),
        os.getenv('TELEGRAM_CHAT_ID')
    )
    return await manager.send_message_with_rate_limit(
        'test',
        'Telegram test message'
    )
