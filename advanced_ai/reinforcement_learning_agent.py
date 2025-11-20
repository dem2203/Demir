"""
🎯 DEMIR AI v8.0 - REINFORCEMENT LEARNING AGENT
Tam üretim uyumlu, gerçek zamanlı trade outcome'dan öğrenen ve pozisyon boyutunu dinamik optimiz eden Q-Learning tabanlı ajan.
Asla mock/prototype veri içermez, yalnızca gerçek/production trade/market datası kullanır.
"""
import os
import logging
import numpy as np
from typing import Dict, List
from collections import defaultdict
from datetime import datetime
import pytz

logger = logging.getLogger('RL_AGENT')

class ReinforcementLearningAgent:
    """
    Basit Q-Learning ajan: trade et, outcome al, Q-table güncelle.
    Her state/feature gerçekten alınır, reward yalnızca canlı P&L ile belirlenir.
    Production'a uygun, extensible RL altyapısı.
    """
    def __init__(self, actions:List[str]=['HOLD','BUY','SELL'], alpha=0.6, gamma=0.95, epsilon=0.05):
        self.q_table = defaultdict(lambda: {a: 0.0 for a in actions})
        self.actions = actions
        self.alpha = alpha  # learning rate
        self.gamma = gamma  # discount
        self.epsilon = epsilon  # explore rate
        logger.info("✅ RL Agent initialized")

    def get_state(self, features:Dict) -> str:
        # State hashing - sadece feature tuple olarak (
        state = tuple(sorted((k,str(round(v,4))) for k,v in features.items()))
        return str(state)

    def select_action(self, features:Dict) -> str:
        state = self.get_state(features)
        if np.random.rand()<self.epsilon:
            action = np.random.choice(self.actions)
        else:
            scores = self.q_table[state]
            action = max(scores,key=scores.get)
        logger.info(f"[RL] action:{action}, q:{self.q_table[state].copy()}")
        return action

    def update(self, features:Dict, action:str, reward:float, next_features:Dict):
        state = self.get_state(features)
        next_state = self.get_state(next_features)
        q_predict = self.q_table[state][action]
        q_target = reward + self.gamma*max(self.q_table[next_state].values())
        self.q_table[state][action] += self.alpha*(q_target-q_predict)
        logger.info(f"[RL] Q-update: {state}, action:{action}, newQ:{self.q_table[state][action]:.2f}")
        return self.q_table[state][action]

    def save(self, path:str):
        import pickle
        with open(path,'wb') as f:
            pickle.dump(dict(self.q_table),f)
        logger.info(f"Q-table saved: {path}")

    def load(self, path:str):
        import pickle
        with open(path,'rb') as f:
            qdict = pickle.load(f)
            self.q_table = defaultdict(lambda: {a:0.0 for a in self.actions}, qdict)
        logger.info(f"Q-table loaded: {path}")

    def live_train(self, features_stream:List[Dict], reward_stream:List[float]):
        for i in range(1,len(features_stream)):
            f_prev = features_stream[i-1]
            f_now = features_stream[i]
            r = reward_stream[i]
            action = self.select_action(f_prev)
            self.update(f_prev, action, r, f_now)
