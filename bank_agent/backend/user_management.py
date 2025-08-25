#!/usr/bin/env python3
"""
User Management System for Banking Agent
Handles user registration, authentication, and session management.
"""

import os
import jwt
import bcrypt
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from fastapi import HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24

# Security
security = HTTPBearer()

@dataclass
class User:
    """User data model."""
    user_id: str
    username: str
    email: str
    first_name: str
    last_name: str
    role: str  # admin, analyst, manager, etc.
    department: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    password_hash: Optional[str] = None

@dataclass
class UserSession:
    """User session data."""
    session_id: str
    user_id: str
    token: str
    created_at: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str

class UserManager:
    """Manages user registration, authentication, and sessions."""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, UserSession] = {}
        self._initialize_default_users()
    
    def _initialize_default_users(self):
        """Initialize with some default users for testing."""
        default_users = [
            {
                "user_id": "admin_001",
                "username": "admin",
                "email": "admin@bank.com",
                "first_name": "Admin",
                "last_name": "User",
                "role": "admin",
                "department": "IT",
                "password": "admin123"
            },
            {
                "user_id": "analyst_001", 
                "username": "analyst",
                "email": "analyst@bank.com",
                "first_name": "Data",
                "last_name": "Analyst",
                "role": "analyst",
                "department": "Analytics",
                "password": "analyst123"
            },
            {
                "user_id": "manager_001",
                "username": "manager", 
                "email": "manager@bank.com",
                "first_name": "Risk",
                "last_name": "Manager",
                "role": "manager",
                "department": "Risk Management",
                "password": "manager123"
            }
        ]
        
        for user_data in default_users:
            self._create_user(
                user_id=user_data["user_id"],
                username=user_data["username"],
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                role=user_data["role"],
                department=user_data["department"],
                password=user_data["password"]
            )
    
    def _create_user(self, user_id: str, username: str, email: str, first_name: str, 
                    last_name: str, role: str, department: str, password: str) -> User:
        """Create a new user."""
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            department=department,
            is_active=True,
            created_at=datetime.now(),
            password_hash=password_hash
        )
        
        self.users[user_id] = user
        logger.info(f"Created user: {username} ({user_id})")
        return user
    
    def register_user(self, username: str, email: str, first_name: str, last_name: str,
                     password: str, role: str = "analyst", department: str = "General") -> Dict[str, Any]:
        """Register a new user."""
        # Check if username or email already exists
        for user in self.users.values():
            if user.username == username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )
            if user.email == email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
        
        # Generate unique user ID
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        
        # Create user
        user = self._create_user(
            user_id=user_id,
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            department=department,
            password=password
        )
        
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "department": user.department,
            "created_at": user.created_at.isoformat()
        }
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        # Find user by username
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break
        
        if not user:
            return None
        
        # Check if user is active
        if not user.is_active:
            return None
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return None
        
        # Update last login
        user.last_login = datetime.now()
        
        return user
    
    def create_session(self, user: User, ip_address: str, user_agent: str) -> UserSession:
        """Create a new user session."""
        session_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(hours=JWT_EXPIRY_HOURS)
        
        # Create JWT token
        payload = {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role,
            "exp": expires_at.timestamp()
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        session = UserSession(
            session_id=session_id,
            user_id=user.user_id,
            token=token,
            created_at=datetime.now(),
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.sessions[session_id] = session
        logger.info(f"Created session for user: {user.username}")
        
        return session
    
    def validate_token(self, token: str) -> Optional[User]:
        """Validate JWT token and return user."""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("user_id")
            
            if not user_id or user_id not in self.users:
                return None
            
            user = self.users[user_id]
            if not user.is_active:
                return None
            
            return user
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def list_users(self, role: Optional[str] = None) -> List[Dict[str, Any]]:
        """List users, optionally filtered by role."""
        users = []
        for user in self.users.values():
            if role and user.role != role:
                continue
            
            users.append({
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "department": user.department,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None
            })
        
        return users
    
    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """Update user information."""
        if user_id not in self.users:
            return None
        
        user = self.users[user_id]
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'email', 'role', 'department', 'is_active']
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(user, field, value)
        
        logger.info(f"Updated user: {user.username}")
        return user
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a user session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False

# Global user manager instance
user_manager = UserManager()

# Dependency functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user from JWT token."""
    token = credentials.credentials
    user = user_manager.validate_token(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_user_optional(request: Request) -> Optional[User]:
    """Get current authenticated user from JWT token (optional - returns None if no valid token)."""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        user = user_manager.validate_token(token)
        return user
    except Exception:
        return None

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def require_role(required_role: str):
    """Decorator to require specific user role."""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return current_user
    return role_checker
