from sqlalchemy import Column, String, Integer
from app.db.database import Base

class SearchEntityConfig(Base):
    __tablename__ = "search_entity_config"
    entity_type = Column(String(50), primary_key=True)
    base_url_route = Column(String(255), nullable=False)
    icon_name = Column(String(50))
    display_priority = Column(Integer, default=10)
