# PHASE 20: llm_context_analyzer.py
# Lokasyon: intelligence_layers/llm_context_analyzer.py

import os
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class LLMContextAnalyzer:
    """Phase 20: Claude for context analysis"""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
            self.enabled = True
        except:
            logger.warning("Claude not available")
            self.enabled = False
    
    async def analyze_market_context(self, macro_factors: Dict, sentiment: Dict) -> Dict:
        """Analyze market context using Claude"""
        if not self.enabled:
            return {"thesis": "Not available", "probability": 0.5}
        
        prompt = f"""
Given these market factors:
Macro: {macro_factors}
Sentiment: {sentiment}

Analyze:
1. Causal relationship?
2. Most likely outcome?
3. What could break this thesis?
4. Risk scenarios?

Be precise. Return JSON: {{"thesis": "...", "probability": 0.X, "target": X, "risks": [...]}}
"""
        
        try:
            response = self.client.messages.create(
                model="claude-3-opus",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            import json
            result = json.loads(response.content[0].text)
            return result
        except Exception as e:
            logger.error(f"Claude error: {e}")
            return {"thesis": "Error", "probability": 0.5}
