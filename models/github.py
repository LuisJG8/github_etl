from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import pika
from datetime import datetime


class RabbitMQ_Data_Validation:
    # ===== MESSAGE METADATA =====
    message_id: Optional[str] = Field(default=None, description="Unique message ID")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # ===== BASIC INFO =====
    id: int = Field(..., description="Repository ID")
    name: str = Field(..., min_length=1, description="Repository name")
    full_name: str = Field(..., description="Full name (owner/repo)")
    description: Optional[str] = None
    github_url: Optional[str] = None
    homepage: Optional[str] = None
    default_branch: str = Field(default="main")
    
    # ===== POPULARITY METRICS =====
    stargazers_count: int = Field(default=0, ge=0)
    forks_count: int = Field(default=0, ge=0)
    watchers_count: int = Field(default=0, ge=0)
    open_issues_count: int = Field(default=0, ge=0)

    # ===== DATES =====
    created_at: datetime
    updated_at: datetime  
    pushed_at: datetime
    
    # ===== REPOSITORY SETTINGS =====
    language: Optional[str] = None
    topics: List[str] = Field(default_factory=list)
    visibility: str = Field(default="public")
    size_kb: int = Field(default=0, ge=0)
    
    # ===== BOOLEAN FLAGS =====
    is_fork: bool = False
    is_archived: bool = False
    is_private: bool = False
    
    # ===== OWNER INFO =====
    owner_login: Optional[str] = None
    owner_type: Optional[str] = None