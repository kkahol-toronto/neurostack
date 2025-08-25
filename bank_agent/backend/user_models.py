#!/usr/bin/env python3
"""
Pydantic models for user management API.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserRegistrationRequest(BaseModel):
    """User registration request model."""
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    role: str = "analyst"
    department: str = "General"

class UserLoginRequest(BaseModel):
    """User login request model."""
    username: str
    password: str

class UserLoginResponse(BaseModel):
    """User login response model."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    first_name: str
    last_name: str
    role: str
    department: str
    expires_at: datetime

class UserProfileResponse(BaseModel):
    """User profile response model."""
    user_id: str
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    department: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

class UserUpdateRequest(BaseModel):
    """User update request model."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None

class UserListResponse(BaseModel):
    """User list response model."""
    users: List[UserProfileResponse]
    total_count: int

class UserBehaviorResponse(BaseModel):
    """User behavior response model."""
    user_id: str
    username: str
    total_queries: int
    preferred_query_types: List[str]
    common_tables: List[str]
    avg_query_complexity: float
    last_activity: datetime
    department: str
    role: str

class UserSessionInfo(BaseModel):
    """User session information."""
    session_id: str
    created_at: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str

class UserSessionsResponse(BaseModel):
    """User sessions response model."""
    user_id: str
    username: str
    active_sessions: List[UserSessionInfo]
    total_sessions: int
