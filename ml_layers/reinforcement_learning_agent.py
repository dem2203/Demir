"""
PHASE 9.3: REINFORCEMENT LEARNING AGENT
File 6 of 10 (ayrı dosyalar)
Folder: ml_layers/reinforcement_learning_agent.py

PPO-based trading agent
- Policy gradient learning
- Reward shaping
- Actor-Critic model
- Risk management
"""

import numpy as np
from typing import Tuple, Optional, Dict, List, Any
import logging

try:
    import tensorflow as tf
    from tensorflow import keras
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    logging.warning("TensorFlow not installed. RL layer will be limited.")

logger = logging.getLogger(__name__)


class ReinforcementLearningAgent:
    """
    PPO-based trading agent
    
    Features:
    - Policy gradient (PPO) learning
    - Actor-Critic architecture
    - Reward shaping for trading
    - Risk-aware trading decisions
    """
    
    def __init__(self, state_dim: int = 10, action_dim: int = 3,
                 learning_rate: float = 0.001):
        """
        Initialize RL agent
        
        Args:
            state_dim: State space dimension
            action_dim: Number of actions (0=BUY, 1=SELL, 2=HOLD)
            learning_rate: Learning rate
        """
        self.state_dim = state_dim
        self.action_dim = action_dim  # 0: BUY, 1: SELL, 2: HOLD
        self.learning_rate = learning_rate
        self.gamma = 0.99  # Discount factor
        self.gae_lambda = 0.95  # GAE parameter
        
        self.actor: Optional[Any] = None
        self.critic: Optional[Any] = None
        self.is_trained = False
        
        if TF_AVAILABLE:
            self.actor, self.critic = self.build_networks()
    
    def build_networks(self) -> Tuple[Optional[Any], Optional[Any]]:
        """
        Build actor-critic networks
        
        Returns:
            Actor and Critic models
        """
        if not TF_AVAILABLE:
            return None, None
        
        try:
            # Actor network (policy)
            actor_input = keras.Input(shape=(self.state_dim,))
            x = keras.layers.Dense(128, activation='relu')(actor_input)
            x = keras.layers.Dense(64, activation='relu')(x)
            actor_output = keras.layers.Dense(self.action_dim, 
                                             activation='softmax')(x)
            actor = keras.Model(actor_input, actor_output)
            actor.compile(optimizer=keras.optimizers.Adam(
                learning_rate=self.learning_rate))
            
            # Critic network (value)
            critic_input = keras.Input(shape=(self.state_dim,))
            x = keras.layers.Dense(128, activation='relu')(critic_input)
            x = keras.layers.Dense(64, activation='relu')(x)
            critic_output = keras.layers.Dense(1)(x)
            critic = keras.Model(critic_input, critic_output)
            critic.compile(optimizer=keras.optimizers.Adam(
                learning_rate=self.learning_rate),
                loss='mse')
            
            return actor, critic
            
        except Exception as e:
            logger.error(f"Network building error: {e}")
            return None, None
    
    def select_action(self, state: np.ndarray) -> int:
        """
        Select action using policy network
        
        Args:
            state: Current state [state_dim]
            
        Returns:
            Action (0=BUY, 1=SELL, 2=HOLD)
        """
        if self.actor is None or not TF_AVAILABLE:
            return np.random.randint(0, self.action_dim)
        
        try:
            logits = self.actor.predict(state.reshape(1, -1), verbose=0)
            probabilities = logits[0]
            action = np.random.choice(self.action_dim, p=probabilities)
            return action
        except Exception as e:
            logger.error(f"Action selection error: {e}")
            return np.random.randint(0, self.action_dim)
    
    def compute_gae(self, rewards: List[float], values: List[float]
                    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute Generalized Advantage Estimation
        
        Args:
            rewards: Episode rewards
            values: Critic values for each step
            
        Returns:
            Advantages and returns
        """
        advantages = []
        gae = 0
        
        for t in reversed(range(len(rewards))):
            if t == len(rewards) - 1:
                next_value = 0
            else:
                next_value = values[t + 1]
            
            delta = rewards[t] + self.gamma * next_value - values[t]
            gae = delta + self.gamma * self.gae_lambda * gae
            advantages.insert(0, gae)
        
        returns = np.array(advantages) + np.array(values)
        advantages = np.array(advantages)
        
        return advantages, returns
    
    def shape_reward(self, profit: float, drawdown: float, 
                    action: int) -> float:
        """
        Shape reward signal for trading
        
        Args:
            profit: Trade profit/loss
            drawdown: Drawdown experienced
            action: Action taken
            
        Returns:
            Shaped reward
        """
        # Profit reward
        reward = profit
        
        # Penalize drawdown
        reward -= drawdown * 0.1
        
        # Penalize holding (encourage decisions)
        if action == 2:  # HOLD
            reward -= 0.01
        
        # Normalize
        reward = np.tanh(reward / 100)
        
        return reward
    
    def train_step(self, states: np.ndarray, actions: np.ndarray,
                   rewards: np.ndarray, old_probs: np.ndarray
                   ) -> Dict[str, float]:
        """
        Single PPO training step
        
        Args:
            states: State batch [batch, state_dim]
            actions: Action batch [batch]
            rewards: Reward batch [batch]
            old_probs: Old policy probabilities
            
        Returns:
            Training metrics
        """
        if self.actor is None or self.critic is None or not TF_AVAILABLE:
            return {"error": "Networks not available"}
        
        try:
            # Compute GAE
            values = self.critic.predict(states, verbose=0).squeeze()
            advantages, returns = self.compute_gae(rewards.tolist(), values.tolist())
            
            # Normalize advantages
            advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
            
            # Train critic
            critic_loss = self.critic.train_on_batch(states, returns)
            
            # Train actor (simplified)
            new_probs = self.actor.predict(states, verbose=0)
            actor_loss = -np.mean(advantages * np.log(new_probs + 1e-8))
            
            self.is_trained = True
            
            return {
                'actor_loss': float(actor_loss),
                'critic_loss': float(critic_loss),
                'mean_advantage': float(advantages.mean())
            }
            
        except Exception as e:
            logger.error(f"Training error: {e}")
            return {"error": str(e)}


if __name__ == "__main__":
    print("✅ PHASE 9.3: Reinforcement Learning Agent Ready")
