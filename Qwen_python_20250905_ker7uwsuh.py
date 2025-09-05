import asyncio
import websockets
import json
import os
from typing import AsyncGenerator

# Get your key from https://polygon.io/dashboard/api-keys
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "your_polygon_api_key_here")

class PolygonLevel2Client:
    def __init__(self):
        self.ws_url = "wss://socket.polygon.io/forex"
        self.symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"]
        self.websocket = None

    async def connect(self) -> AsyncGenerator[dict, None]:
        """Connect to Polygon.io Level 2 feed"""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            
            # Authenticate
            auth_msg = {"action": "auth", "params": POLYGON_API_KEY}
            await self.websocket.send(json.dumps(auth_msg))
            
            # Subscribe to Level 2 data
            for symbol in self.symbols:
                sub_msg = {"action": "subscribe", "params": f"Q.{symbol}"}
                await self.websocket.send(json.dumps(sub_msg))
            
            print("✅ Connected to Polygon.io Level 2 feed")
            
            while True:
                try:
                    message = await self.websocket.recv()
                    data = json.loads(message)
                    
                    if data[0]["ev"] == "status":
                        continue
                    
                    for quote in data:
                        if quote.get("ev") == "Q":
                            yield {
                                "symbol": quote["p"].replace("USD", "/USD"),
                                "bid": quote["bP"],
                                "ask": quote["aP"],
                                "bid_size": quote["bS"],
                                "ask_size": quote["aS"],
                                "timestamp": quote["t"]
                            }
                except websockets.ConnectionClosed:
                    print("⚠️ Connection lost. Reconnecting...")
                    await asyncio.sleep(5)
                    await self.connect()
                    
        except Exception as e:
            print(f"❌ Polygon client error: {e}")
            await asyncio.sleep(5)
            await self.connect()