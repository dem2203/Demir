# FILE 1: regulatory_news_parser.py
# Lokasyon: intelligence_layers/regulatory_news_parser.py

import os
import asyncio
import logging
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class RegulatoryNewsParser:
    """Phase 17: Regulatory news tracking + sentiment analysis"""
    
    def __init__(self):
        self.newsapi_key = os.getenv("NEWSAPI_KEY", "")
        
        try:
            from transformers import pipeline
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert"
            )
            self.has_finbert = True
        except ImportError:
            logger.warning("FinBERT not installed. Using basic sentiment.")
            self.has_finbert = False
        
        self.last_alert = {}
    
    async def fetch_regulatory_news(self) -> List[Dict]:
        """Fetch crypto-related regulatory news"""
        try:
            if not self.newsapi_key:
                logger.warning("NewsAPI key not configured")
                return []
            
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": "cryptocurrency regulation OR SEC OR CFTC OR crypto",
                "sortBy": "publishedAt",
                "language": "en",
                "apiKey": self.newsapi_key,
                "pageSize": 50,
            }
            
            response = requests.get(url, params=params, timeout=10)
            articles = response.json().get("articles", [])
            
            news_list = []
            for article in articles:
                sentiment, score = await self.analyze_sentiment(article["title"])
                
                news_list.append({
                    "title": article["title"],
                    "source": article["source"]["name"],
                    "url": article["url"],
                    "published_at": article["publishedAt"],
                    "sentiment": sentiment,
                    "score": score,
                    "description": article["description"],
                })
            
            return sorted(news_list, key=lambda x: x["score"], reverse=True)
        
        except Exception as e:
            logger.error(f"News fetch error: {e}")
            return []
    
    async def analyze_sentiment(self, text: str) -> tuple:
        """Analyze text sentiment using FinBERT"""
        try:
            if not self.has_finbert:
                negative_words = ["crash", "ban", "illegal", "fraud", "death"]
                positive_words = ["approve", "bullish", "adoption", "success"]
                
                text_lower = text.lower()
                neg_count = sum(1 for word in negative_words if word in text_lower)
                pos_count = sum(1 for word in positive_words if word in text_lower)
                
                if neg_count > pos_count:
                    return "NEGATIVE", 0.7 if neg_count > 1 else 0.5
                elif pos_count > neg_count:
                    return "POSITIVE", 0.7 if pos_count > 1 else 0.5
                else:
                    return "NEUTRAL", 0.5
            
            result = self.sentiment_analyzer(text[:512])[0]
            label = result["label"].upper()
            score = result["score"]
            
            return label, score
        
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return "NEUTRAL", 0.5
    
    async def get_high_impact_news(self, threshold: float = 0.7) -> List[Dict]:
        """Get high-impact regulatory news"""
        news = await self.fetch_regulatory_news()
        
        high_impact = []
        for item in news:
            if item["sentiment"] == "NEGATIVE" and item["score"] > threshold:
                high_impact.append(item)
        
        return high_impact
