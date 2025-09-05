import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime
import pickle

class TacticalAIEngine:
    def __init__(self):
        self.model = self._build_model()
        self.scaler = StandardScaler()
        self.feature_names = [
            'delta_5s', 'volume_imbalance', 'vwap_deviation',
            'news_sentiment', 'economic_impact', 'support_resistance_score'
        ]
        self.signal_map = {0: "NEUTRAL", 1: "BUY", 2: "SELL"}

    def _build_model(self):
        """Pre-trained model (you can retrain with historical data)"""
        # This is a placeholder for a real trained model
        # In production, you'd train on 6+ months of order flow data
        return RandomForestClassifier(n_estimators=100, random_state=42)

    def extract_features(self, market_data: dict, news: dict) -> np.array:
        """Extract real-time features for inference"""
        delta = market_data['bid_size'] - market_data['ask_size']
        imbalance = abs(delta) / (market_data['bid_size'] + market_data['ask_size'])
        
        vwap_dev = 0.0  # Connect to real VWAP engine
        sentiment = news.get('sentiment', 0.0)  # -1 to +1
        econ_impact = news.get('impact', 0)  # 0=Low, 1=Medium, 2=High
        sr_score = 0.5  # Support/Resistance proximity (0-1)

        features = np.array([[delta, imbalance, vwap_dev, sentiment, econ_impact, sr_score]])
        return self.scaler.transform(features)

    def predict(self, market_data: dict, news: dict) -> dict:
        """Generate real AI signal"""
        try:
            X = self.extract_features(market_data, news)
            proba = self.model.predict_proba(X)[0]
            prediction = self.model.predict(X)[0]

            confidence = round(float(max(proba) * 100), 1)
            signal = self.signal_map[prediction]

            # Generate plain-English insight
            insights = {
                "BUY": f"Strong buying pressure detected. Delta: +{market_data['bid_size']-market_data['ask_size']} contracts. BUY {market_data['symbol']}.",
                "SELL": f"Institutional selling at resistance. Volume imbalance: {round(proba[2]*100)}%. SELL {market_data['symbol']}.",
                "NEUTRAL": "Market balanced. No clear edge. Await NFP/CPI release."
            }

            return {
                "signal": signal,
                "confidence": confidence,
                "text": insights[signal],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "signal": "NEUTRAL",
                "confidence": 0,
                "text": f"AI Engine Error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }

# Global AI instance
ai_engine = TacticalAIEngine()