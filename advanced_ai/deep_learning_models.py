"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DeepLearningModels - DEMIR AI Enterprise (Production-Safe)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Production fallback - TensorFlow opsiyonel. Gerçek TensorFlow yüklü değilse sistem crash yapmaz, AI normal çalışmaya devam eder.
Pro trader kurallarına %100 uyum: Asla sahte-sinyal üretmez!
"""

import logging

logger = logging.getLogger(__name__)

try:
    import tensorflow as tf
    HAS_TENSORFLOW = True
    logger.info("DeepLearningModels: TensorFlow detected (full features enabled)")
except ImportError:
    HAS_TENSORFLOW = False
    logger.warning("DeepLearningModels: TensorFlow NOT installed - deep layers/passive")

if HAS_TENSORFLOW:
    class DeepLearningModels:
        """Real TensorFlow-based models (PROD not active - dev only)"""
        def __init__(self):
            self.model = None
        def load_model(self, model_path):
            self.model = tf.keras.models.load_model(model_path)
        def predict(self, inputs):
            if self.model is None:
                raise Exception("Model not loaded")
            return self.model.predict(inputs)
else:
    class DeepLearningModels:
        """Dummy DeepLearningModels; prod mode, all infer ops disabled (TensorFlow not available)"""
        def __init__(self, *args, **kwargs):
            pass
        def load_model(self, *args, **kwargs):
            logger.info("DeepLearningModels.load_model: skipped (TensorFlow not present)")
        def predict(self, *args, **kwargs):
            logger.warning("DeepLearningModels.predict: disabled (TensorFlow not installed)")
            raise NotImplementedError(
                "DeepLearningModels.predict: NOOP (TensorFlow not present). Prod trade unaffected."
            )
