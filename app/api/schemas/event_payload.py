from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

class EventPayload(BaseModel):
    # Restrict actions to specific strings
    event_action: Literal["CREATE", "UPDATE", "DELETE"] 
    
    entity_type: str
    entity_id: str
    
    title: Optional[str] = None
    subtitle: Optional[str] = None
    status: Optional[str] = None
    
    # Unified company handling
    company_id: Optional[int] = None
    company_ids: Optional[List[int]] = Field(default_factory=list)
    allowed_branch_ids: Optional[List[int]] = Field(default_factory=list)
    
    search_text: Optional[str] = ""
    
    # Critical for 3M records management
    timestamp: datetime = Field(default_factory=datetime.utcnow)
