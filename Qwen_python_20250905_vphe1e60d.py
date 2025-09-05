from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from polygon_client import PolygonLevel2Client
from ai_engine import ai_engine

app = FastAPI(title="AEGIS FLOW API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global clients
polygon_client = PolygonLevel2Client()
active_connections = []

@app.on_event("startup")
async def startup_event():
    print("🚀 AEGIS FLOW Backend Starting...")
    # Start background data fetcher
    asyncio.create_task(stream_polygon_data())

@app.get("/health")
async def health_check():
    return {"status": "alive", "service": "aegis-flow-backend"}

@app.get("/api/symbols")
async def get_symbols():
    return ["EUR/USD", "GBP/USD", "USD/JPY", "XAU/USD", "BTC/USD"]

@app.websocket("/ws/market-data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        async for data in polygon_client.connect():
            await websocket.send_text(json.dumps({
                "type": "market_data",
                "data": data
            }))
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)

@app.websocket("/ws/ai-insights")
async def ai_websocket(websocket: WebSocket):
    await websocket.accept()
    
    # Mock news sentiment (connect to Bloomberg/Reuters API)
    news_context = {"sentiment": 0.3, "impact": 1}
    
    while True:
        try:
            async for market_data in polygon_client.connect():
                insight = ai_engine.predict(market_data, news_context)
                await websocket.send_text(json.dumps(insight))
                await asyncio.sleep(1)  # Update every second
        except:
            await asyncio.sleep(5)

async def stream_polygon_data():
    """Background task to fetch real data"""
    async for data in polygon_client.connect():
        pass  # Store in DB or cache