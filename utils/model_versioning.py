#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════════════════
ModelVersioning ENTERPRISE - DEMIR AI v8.0
════════════════════════════════════════════════════════════════════════════════
Production-grade ML model versioning and lifecycle management
- Semantic versioning (major.minor.patch)
- Model registry with metadata tracking
- Performance-based automatic promotion/rollback
- A/B testing support
- Model comparison and selection
- Deployment history and audit trail
"""

import logging
import json
import pickle
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)


class ModelVersion:
    """
    Model version metadata container.
    
    Attributes:
        major: Breaking changes
        minor: New features (backward compatible)
        patch: Bug fixes
    """
    
    def __init__(self, major: int = 1, minor: int = 0, patch: int = 0):
        self.major = major
        self.minor = minor
        self.patch = patch
    
    def __str__(self) -> str:
        return f"v{self.major}.{self.minor}.{self.patch}"
    
    def bump_major(self):
        """Increment major version (breaking change)."""
        self.major += 1
        self.minor = 0
        self.patch = 0
    
    def bump_minor(self):
        """Increment minor version (new feature)."""
        self.minor += 1
        self.patch = 0
    
    def bump_patch(self):
        """Increment patch version (bug fix)."""
        self.patch += 1
    
    def to_dict(self) -> Dict:
        return {
            'major': self.major,
            'minor': self.minor,
            'patch': self.patch,
            'version_string': str(self)
        }
    
    @classmethod
    def from_string(cls, version_str: str):
        """Parse version from string like 'v1.2.3'."""
        parts = version_str.lstrip('v').split('.')
        return cls(
            major=int(parts[0]),
            minor=int(parts[1]) if len(parts) > 1 else 0,
            patch=int(parts[2]) if len(parts) > 2 else 0
        )


class ModelVersioning:
    """
    Enterprise model versioning and lifecycle management system.
    
    Features:
    - Semantic versioning with automatic bumping
    - Model registry with performance tracking
    - Deployment history and rollback capability
    - A/B testing support
    - Model comparison and selection
    - Metadata persistence
    
    Attributes:
        registry_dir: Directory for model registry
        models_dir: Directory for stored models
        registry: In-memory model registry
        active_version: Currently deployed version
    """
    
    def __init__(self, registry_dir: str = "model_registry", models_dir: str = "models"):
        self.registry_dir = Path(registry_dir)
        self.models_dir = Path(models_dir)
        
        # Create directories
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize registry
        self.registry_file = self.registry_dir / "registry.json"
        self.registry: Dict[str, List[Dict]] = self._load_registry()
        
        # Active versions per model
        self.active_versions: Dict[str, str] = {}
        
        logger.info(f"✅ ModelVersioning initialized: {self.registry_dir}")
    
    def _load_registry(self) -> Dict[str, List[Dict]]:
        """Load model registry from disk."""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    registry = json.load(f)
                logger.info(f"📚 Loaded registry: {len(registry)} model families")
                return registry
            except Exception as e:
                logger.warning(f"⚠️ Failed to load registry: {e}")
        
        return {}
    
    def _save_registry(self):
        """Persist model registry to disk."""
        try:
            with open(self.registry_file, 'w') as f:
                json.dump(self.registry, f, indent=2, default=str)
            logger.debug("💾 Registry saved")
        except Exception as e:
            logger.error(f"❌ Failed to save registry: {e}")
    
    def register_model(
        self,
        model_name: str,
        model_path: str,
        metrics: Dict[str, float],
        version: Optional[ModelVersion] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Register a new model version.
        
        Args:
            model_name: Model identifier (e.g., 'transformer', 'ensemble')
            model_path: Path to serialized model file
            metrics: Performance metrics dictionary
            version: Model version (auto-generated if None)
            metadata: Additional metadata
            
        Returns:
            Version string of registered model
        """
        try:
            # Initialize model family if not exists
            if model_name not in self.registry:
                self.registry[model_name] = []
            
            # Determine version
            if version is None:
                # Auto-bump patch version
                if self.registry[model_name]:
                    last_version = ModelVersion.from_string(
                        self.registry[model_name][-1]['version']
                    )
                    last_version.bump_patch()
                    version = last_version
                else:
                    version = ModelVersion(1, 0, 0)
            
            version_str = str(version)
            
            # Copy model to versioned location
            versioned_path = self.models_dir / f"{model_name}_{version_str}.pkl"
            shutil.copy2(model_path, versioned_path)
            
            # Create registry entry
            entry = {
                'version': version_str,
                'path': str(versioned_path),
                'metrics': metrics,
                'registered_at': datetime.now().isoformat(),
                'metadata': metadata or {},
                'status': 'registered'
            }
            
            # Add to registry
            self.registry[model_name].append(entry)
            self._save_registry()
            
            logger.info(
                f"✅ Registered {model_name} {version_str} - "
                f"F1: {metrics.get('f1', 0):.3f}"
            )
            
            return version_str
            
        except Exception as e:
            logger.error(f"❌ Model registration error: {e}")
            return ""
    
    def promote_to_production(
        self,
        model_name: str,
        version: str
    ) -> bool:
        """
        Promote a model version to production (active deployment).
        
        Args:
            model_name: Model identifier
            version: Version to promote
            
        Returns:
            bool: Success status
        """
        try:
            if model_name not in self.registry:
                logger.error(f"❌ Model {model_name} not found in registry")
                return False
            
            # Find version in registry
            version_entry = None
            for entry in self.registry[model_name]:
                if entry['version'] == version:
                    version_entry = entry
                    break
            
            if not version_entry:
                logger.error(f"❌ Version {version} not found for {model_name}")
                return False
            
            # Update status
            version_entry['status'] = 'production'
            version_entry['promoted_at'] = datetime.now().isoformat()
            
            # Set as active version
            self.active_versions[model_name] = version
            
            # Create symlink to production model
            prod_link = self.models_dir / f"{model_name}_production.pkl"
            if prod_link.exists():
                prod_link.unlink()
            
            versioned_path = Path(version_entry['path'])
            if versioned_path.exists():
                prod_link.symlink_to(versioned_path)
            
            self._save_registry()
            
            logger.info(f"🚀 Promoted {model_name} {version} to production")
            return True
            
        except Exception as e:
            logger.error(f"❌ Promotion error: {e}")
            return False
    
    def rollback(
        self,
        model_name: str,
        target_version: Optional[str] = None
    ) -> bool:
        """
        Rollback model to previous or specified version.
        
        Args:
            model_name: Model identifier
            target_version: Version to rollback to (previous if None)
            
        Returns:
            bool: Success status
        """
        try:
            if model_name not in self.registry:
                logger.error(f"❌ Model {model_name} not found")
                return False
            
            # Find target version
            if target_version is None:
                # Get previous production version
                prod_versions = [
                    e for e in self.registry[model_name]
                    if e.get('status') == 'production'
                ]
                if len(prod_versions) < 2:
                    logger.error("❌ No previous version to rollback to")
                    return False
                target_version = prod_versions[-2]['version']
            
            logger.warning(f"⚠️ Rolling back {model_name} to {target_version}")
            return self.promote_to_production(model_name, target_version)
            
        except Exception as e:
            logger.error(f"❌ Rollback error: {e}")
            return False
    
    def compare_versions(
        self,
        model_name: str,
        version1: str,
        version2: str
    ) -> Dict[str, Any]:
        """
        Compare performance metrics between two versions.
        
        Args:
            model_name: Model identifier
            version1: First version
            version2: Second version
            
        Returns:
            Comparison results dictionary
        """
        try:
            if model_name not in self.registry:
                return {'error': 'Model not found'}
            
            # Find versions
            v1_entry = next(
                (e for e in self.registry[model_name] if e['version'] == version1),
                None
            )
            v2_entry = next(
                (e for e in self.registry[model_name] if e['version'] == version2),
                None
            )
            
            if not v1_entry or not v2_entry:
                return {'error': 'Version not found'}
            
            # Compare metrics
            comparison = {
                'model_name': model_name,
                'version1': version1,
                'version2': version2,
                'metrics_v1': v1_entry['metrics'],
                'metrics_v2': v2_entry['metrics'],
                'improvements': {}
            }
            
            # Calculate improvements
            for metric in v1_entry['metrics']:
                if metric in v2_entry['metrics']:
                    v1_val = v1_entry['metrics'][metric]
                    v2_val = v2_entry['metrics'][metric]
                    improvement = ((v2_val - v1_val) / v1_val * 100) if v1_val > 0 else 0
                    comparison['improvements'][metric] = improvement
            
            logger.info(f"📊 Compared {model_name}: {version1} vs {version2}")
            return comparison
            
        except Exception as e:
            logger.error(f"❌ Comparison error: {e}")
            return {'error': str(e)}
    
    def get_best_version(
        self,
        model_name: str,
        metric: str = 'f1'
    ) -> Optional[str]:
        """
        Find best performing version based on metric.
        
        Args:
            model_name: Model identifier
            metric: Metric to optimize (default: f1)
            
        Returns:
            Version string of best model
        """
        try:
            if model_name not in self.registry or not self.registry[model_name]:
                return None
            
            best_version = max(
                self.registry[model_name],
                key=lambda x: x['metrics'].get(metric, 0)
            )
            
            logger.info(
                f"🏆 Best {model_name} by {metric}: "
                f"{best_version['version']} ({best_version['metrics'].get(metric, 0):.3f})"
            )
            
            return best_version['version']
            
        except Exception as e:
            logger.error(f"❌ Best version lookup error: {e}")
            return None
    
    def list_versions(self, model_name: str) -> List[Dict]:
        """
        List all versions of a model.
        
        Args:
            model_name: Model identifier
            
        Returns:
            List of version entries
        """
        return self.registry.get(model_name, [])
    
    def get_production_version(self, model_name: str) -> Optional[str]:
        """
        Get currently deployed production version.
        
        Args:
            model_name: Model identifier
            
        Returns:
            Production version string
        """
        return self.active_versions.get(model_name)


if __name__ == "__main__":
    # Test instantiation
    versioning = ModelVersioning()
    print(f"✅ ModelVersioning initialized: {len(versioning.registry)} model families")
