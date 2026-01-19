from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


class RabbitMQ_Data_Validation(BaseModel):
    # ===== MESSAGE METADATA =====
    message_id: str
    got_data_in: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # ===== BASIC INFO =====
    repo_id: int
    name: str 
    full_name: str 
    description: Optional[str] = None
    github_url: Optional[str] = None
    homepage: Optional[str] = None
    default_branch: str
    
    # ===== POPULARITY METRICS =====
    stargazers_count: int = Field(default=0, ge=0)
    forks_count: int = Field(default=0, ge=0)
    watchers_count: int = Field(default=0, ge=0)
    open_issues_count: int = Field(default=0, ge=0)

    # ===== DATES =====
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    pushed_at: Optional[datetime] = None
    
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