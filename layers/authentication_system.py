# ============================================================================
# LAYER 7: AUTHENTICATION SYSTEM (YENİ DOSYA)
# ============================================================================
# Dosya: Demir/layers/authentication_system_v5.py
# Durum: YENİ (eski mock versiyonunu replace et)

import jwt
from datetime import datetime, timedelta
import hashlib
import secrets

class AuthenticationSystem:
    """
    Real JWT authentication system
    - Token generation
    - Token validation
    - User management
    - API key authentication
    - ZERO mock auth!
    """
    
    def __init__(self, secret_key: str = None):
        """Initialize with real secret key"""
        
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
        self.algorithm = 'HS256'
        self.token_expiry_hours = 24
        
        logger.info("✅ AuthenticationSystem initialized")
    
    def generate_token(self, user_id: str, api_key: str = None) -> str:
        """
        Generate REAL JWT token
        - NOT mock token
        - Proper signing
        """
        
        payload = {
            'user_id': user_id,
            'api_key': api_key,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours)
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.info(f"✅ Token generated for user: {user_id}")
        
        return token
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate REAL JWT token
        - NOT mock validation
        - Real signature check
        """
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            logger.info(f"✅ Token valid for user: {payload['user_id']}")
            return payload
            
        except jwt.ExpiredSignatureError:
            error = "Token expired"
            logger.error(error)
            raise ValueError(error)
        except jwt.InvalidTokenError as e:
            error = f"Invalid token: {e}"
            logger.error(error)
            raise ValueError(error)
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash API key for storage"""
        
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def verify_api_key(self, api_key: str, hashed_key: str) -> bool:
        """Verify API key against hash"""
        
        return self.hash_api_key(api_key) == hashed_key
