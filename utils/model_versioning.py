import logging
import os
import json
from datetime import datetime
import pickle
import shutil

logger = logging.getLogger(__name__)

class ModelVersionManager:
    """
    Model version control - track all model versions
    Auto-deploy better versions
    Rollback if degradation
    """
    
    def __init__(self, version_dir: str = "models/versions"):
        self.version_dir = version_dir
        os.makedirs(version_dir, exist_ok=True)
        self.metadata_file = os.path.join(version_dir, "metadata.json")
        
    def save_model(self, model, model_type: str, metrics: dict) -> str:
        """Save model with metadata"""
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = os.path.join(self.version_dir, f"{model_type}_v{version}.pkl")
        
        # Save model
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        # Save metadata
        metadata = {
            'version': version,
            'type': model_type,
            'saved_at': datetime.now().isoformat(),
            'metrics': metrics,
            'path': model_path
        }
        
        self._update_metadata(metadata)
        
        logger.info(f"✅ Model saved: {model_type}_v{version}")
        return version
    
    def get_best_model(self, model_type: str):
        """Get best performing model"""
        metadata = self._load_metadata()
        
        models = [m for m in metadata if m['type'] == model_type]
        if not models:
            return None
        
        best = max(models, key=lambda x: x['metrics'].get('accuracy', 0))
        
        with open(best['path'], 'rb') as f:
            model = pickle.load(f)
        
        return model
    
    def rollback_model(self, model_type: str, version: str):
        """Rollback to previous model"""
        metadata = self._load_metadata()
        
        target = next((m for m in metadata if m['type'] == model_type and m['version'] == version), None)
        if target:
            logger.info(f"🔄 Rolling back to {model_type}_v{version}")
            return target
        
        return None
    
    def _load_metadata(self):
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file) as f:
                return json.load(f)
        return []
    
    def _update_metadata(self, metadata):
        all_metadata = self._load_metadata()
        all_metadata.append(metadata)
        
        with open(self.metadata_file, 'w') as f:
            json.dump(all_metadata, f, indent=2)
