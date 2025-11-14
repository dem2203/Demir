# DEMIR AI - Model Storage

This directory stores all ML models used by DEMIR AI.

## Directory Structure

```
models/
├── versions/          # All model versions with metadata
│   ├── metadata.json  # Tracking file for all models
│   └── *.pkl          # Pickled model files
│
├── v1.0/             # Stable release v1.0
├── v1.1/             # Stable release v1.1
└── ...               # Future versions
```

## Model Types

1. **Transformer** (transformer_v*.pkl)
   - Time series prediction
   - Multi-head attention
   - 256 embedding dimensions

2. **Ensemble** (ensemble_v*.pkl)
   - LSTM + GRU + XGBoost + LightGBM + RandomForest
   - Voting mechanism
   - Meta-learner combination

3. **DQN** (dqn_v*.pkl)
   - Deep Q-Network
   - Reinforcement learning
   - Policy optimization

## Versioning

Models are versioned with timestamps: `YYYYMMDD_HHMMSS`

Example: `transformer_v20251114_220000.pkl`

## Metadata Format

```json
{
  "version": "20251114_220000",
  "type": "transformer",
  "saved_at": "2025-11-14T22:00:00Z",
  "metrics": {
    "accuracy": 0.85,
    "loss": 0.12,
    "win_rate": 0.72
  },
  "path": "models/versions/transformer_v20251114_220000.pkl"
}
```

## Usage

```python
from utils.model_versioning import ModelVersionManager

# Initialize
manager = ModelVersionManager(version_dir="models/versions")

# Save new model
version = manager.save_model(
    model=transformer,
    model_type='transformer',
    metrics={'accuracy': 0.85, 'loss': 0.12}
)

# Load best model
best_model = manager.get_best_model('transformer')

# Rollback to previous version
manager.rollback_model('transformer', '20251114_210000')
```

## Automatic Cleanup

Old models (>30 days) are automatically archived to keep storage manageable.

## Backups

All models are backed up daily to Railway's persistent storage.
