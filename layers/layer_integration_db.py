# ============================================================================
# LAYER 8: LAYER INTEGRATION DB (YENİ DOSYA)
# ============================================================================
# Dosya: Demir/layers/layer_integration_db_v5.py
# Durum: YENİ

class LayerIntegrationDatabase:
    """
    Database integration for all 62 layers
    - Store layer configurations
    - Track layer status
    - Store layer outputs
    """
    
    def __init__(self, db_layer: PostgreSQLDatabaseLayer):
        self.db = db_layer
        logger.info("✅ LayerIntegrationDatabase initialized")
    
    def save_layer_output(self, layer_name: str, output: Dict[str, Any]):
        """Save layer output to database"""
        
        conn = self.db.pool.getconn()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO layer_performance (layer_name, accuracy, latency_ms)
                VALUES (%s, %s, %s)
            """, (
                layer_name,
                output.get('score', 50),
                output.get('latency', 0)
            ))
            
            conn.commit()
            logger.debug(f"Layer output saved: {layer_name}")
            
        except Exception as e:
            logger.error(f"Failed to save layer output: {e}")
            conn.rollback()
        finally:
            self.db.pool.putconn(conn)
