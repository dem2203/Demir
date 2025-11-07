"""
PHASE 5.1: AUTHENTICATION SYSTEM
File 1 of 10 (ayrı dosyalar)
Folder: layers/authentication_system.py

JWT-based authentication system for Streamlit/API
- User registration & login
- Password hashing with bcrypt
- Token generation & validation
"""

import os
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import logging
from functools import wraps
import bcrypt

logger = logging.getLogger(__name__)


class AuthenticationSystem:
    """
    JWT-based authentication layer
    
    Features:
    - User registration/login
    - Token generation & validation
    - Password hashing (bcrypt)
    - Token refresh
    - Role-based access control
    """
    
    def __init__(self, secret_key: Optional[str] = None, expiration_hours: int = 24):
        """
        Initialize authentication system
        
        Args:
            secret_key: JWT secret key (from env or parameter)
            expiration_hours: Token validity duration
        """
        self.secret_key = secret_key or os.getenv('JWT_SECRET', 'dev-secret-key-change-prod')
        self.expiration_hours = expiration_hours
        self.users_db: Dict[str, Dict[str, Any]] = {}
        self.blacklist: set = set()
        
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode(), salt).decode()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode(), hashed.encode())
    
    def register_user(self, username: str, password: str, email: str, 
                      role: str = "user") -> Dict[str, Any]:
        """
        Register new user
        
        Args:
            username: Unique username
            password: User password
            email: User email
            role: User role (user/admin)
            
        Returns:
            Registration result
        """
        if username in self.users_db:
            return {"success": False, "message": "Username already exists"}
        
        if len(password) < 8:
            return {"success": False, "message": "Password must be at least 8 characters"}
        
        try:
            hashed_pwd = self.hash_password(password)
            self.users_db[username] = {
                "password": hashed_pwd,
                "email": email,
                "role": role,
                "created_at": datetime.utcnow().isoformat(),
                "active": True
            }
            logger.info(f"User registered: {username}")
            return {"success": True, "message": "User registered successfully"}
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return {"success": False, "message": str(e)}
    
    def generate_token(self, username: str, password: str) -> Optional[str]:
        """
        Generate JWT token for login
        
        Args:
            username: Username
            password: Plain password
            
        Returns:
            JWT token or None if auth failed
        """
        if username not in self.users_db:
            logger.warning(f"Login attempt - user not found: {username}")
            return None
        
        user = self.users_db[username]
        
        if not user.get('active'):
            logger.warning(f"Login attempt - inactive user: {username}")
            return None
        
        if not self.verify_password(password, user['password']):
            logger.warning(f"Login attempt - wrong password: {username}")
            return None
        
        try:
            payload = {
                'username': username,
                'email': user['email'],
                'role': user['role'],
                'exp': datetime.utcnow() + timedelta(hours=self.expiration_hours),
                'iat': datetime.utcnow()
            }
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            logger.info(f"Token generated for: {username}")
            return token
        except Exception as e:
            logger.error(f"Token generation error: {e}")
            return None
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token
            
        Returns:
            Decoded payload or None if invalid
        """
        if token in self.blacklist:
            logger.warning("Token is blacklisted")
            return None
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def refresh_token(self, token: str) -> Optional[str]:
        """Refresh an existing token"""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        username = payload.get('username')
        if not username or username not in self.users_db:
            return None
        
        self.blacklist.add(token)
        return self.generate_token(username, self.users_db[username]['password'])
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a token"""
        self.blacklist.add(token)
        return True
    
    def require_auth(self, func):
        """Decorator for protected functions"""
        @wraps(func)
        def wrapper(token: str = None, *args, **kwargs):
            if not token:
                return {"error": "Token required"}
            
            payload = self.verify_token(token)
            if not payload:
                return {"error": "Unauthorized"}
            
            return func(*args, username=payload['username'], 
                       role=payload.get('role'), **kwargs)
        return wrapper


if __name__ == "__main__":
    print("✅ PHASE 5.1: Authentication System Ready")
