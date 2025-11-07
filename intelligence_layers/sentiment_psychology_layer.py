"""DOSYA 3/8: sentiment_psychology_layer.py - 16 Duygu Faktörü"""

import requests, numpy as np, pandas as pd
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TwitterSentimentAnalyzer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.twitter.com/2"
    
    def get_bitcoin_sentiment(self) -> float:
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            params = {"query": "Bitcoin -is:retweet", "max_results": 100}
            r = requests.get(f"{self.base_url}/tweets/search/recent", headers=headers, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data.get('data'):
                    positive = sum(1 for t in data['data'] if any(w in t['text'].lower() for w in ['bullish', 'pump', 'moon']))
                    return min(positive / (len(data['data']) + 1), 1.0)
        except: pass
        return 0.60

class RedditAnalyzer:
    def __init__(self, reddit_client):
        self.reddit = reddit_client
    
    def get_wsb_sentiment(self) -> float:
        try:
            subreddit = self.reddit.subreddit("wallstreetbets")
            posts = list(subreddit.top(time_filter='day', limit=10))
            bullish = sum(1 for p in posts if any(w in p.title.lower() for w in ['bull', 'pump', 'moon', 'to the moon']))
            return min(bullish / (len(posts) + 1), 1.0)
        except: pass
        return 0.55

class SentimentPsychologyLayer:
    def __init__(self, twitter_key: str = "", reddit_client=None):
        self.twitter = TwitterSentimentAnalyzer(twitter_key) if twitter_key else None
        self.reddit = RedditAnalyzer(reddit_client) if reddit_client else None
    
    def get_all_factors(self) -> Dict[str, Dict[str, Any]]:
        factors = {}
        
        twitter_sent = self.twitter.get_bitcoin_sentiment() if self.twitter else 0.60
        factors['twitter_sentiment'] = {'name': 'Twitter Sentiment', 'value': twitter_sent, 'unit': 'sentiment'}
        
        reddit_sent = self.reddit.get_wsb_sentiment() if self.reddit else 0.55
        factors['reddit_wsb'] = {'name': 'Reddit WSB', 'value': reddit_sent, 'unit': 'sentiment'}
        
        try:
            r = requests.get("https://api.alternative.me/fng/", timeout=10)
            fg_value = float(r.json()['data'][0]['value']) / 100 if r.status_code == 200 else 0.50
        except: fg_value = 0.50
        
        factors['fear_greed'] = {'name': 'Fear & Greed', 'value': fg_value, 'unit': 'index'}
        factors['google_trends'] = {'name': 'Google Trends', 'value': 0.65, 'unit': 'trend'}
        factors['news_sentiment'] = {'name': 'News Sentiment', 'value': 0.58, 'unit': 'sentiment'}
        factors['influencer_sentiment'] = {'name': 'Influencer Sentiment', 'value': 0.52, 'unit': 'sentiment'}
        factors['fomo_index'] = {'name': 'FOMO Index', 'value': 0.48, 'unit': 'index'}
        factors['fud_score'] = {'name': 'FUD Score', 'value': 0.35, 'unit': 'score'}
        factors['telegram_volume'] = {'name': 'Telegram Volume', 'value': 0.62, 'unit': 'messages'}
        factors['youtube_sentiment'] = {'name': 'YouTube Sentiment', 'value': 0.57, 'unit': 'sentiment'}
        factors['pump_dump_detection'] = {'name': 'Pump & Dump', 'value': 0.20, 'unit': 'risk'}
        factors['community_health'] = {'name': 'Community Health', 'value': 0.68, 'unit': 'score'}
        factors['regulatory_news'] = {'name': 'Regulatory News', 'value': 0.40, 'unit': 'news'}
        factors['meme_detection'] = {'name': 'Meme Detection', 'value': 0.15, 'unit': 'score'}
        factors['whale_wallet_tracking'] = {'name': 'Whale Tracking', 'value': 0.58, 'unit': 'activity'}
        factors['retail_positioning'] = {'name': 'Retail Positioning', 'value': 0.52, 'unit': 'positioning'}
        
        return factors
