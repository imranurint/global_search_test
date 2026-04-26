import uuid
from sqlalchemy import Column, String, Integer, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY, TSVECTOR
from app.db.database import Base

class GlobalSearchIndex(Base):
    __tablename__ = "global_search_index"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(100), nullable=False)
    
    title = Column(String(255), nullable=False)
    subtitle = Column(String(255))
    status = Column(String(100))
    
    company_id = Column(Integer, nullable=False)
    allowed_branch_ids = Column(ARRAY(Integer), nullable=True) 
    
    search_vector = Column(TSVECTOR)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_global_search_entity', 'entity_type', 'entity_id', unique=True),
        Index('idx_global_search_company', 'company_id'),
        Index('idx_global_search_vector', 'search_vector', postgresql_using='gin'),
    )
