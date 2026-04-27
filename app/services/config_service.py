from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.entity_config import SearchEntityConfig
from typing import List, Optional

class ConfigService:
    @staticmethod
    def get_all_configs(db: Session):
        return db.query(SearchEntityConfig).all()

    @staticmethod
    def create_config(db: Session, entity_type: str, base_url_route: str, icon_name: Optional[str] = None):
        existing = db.query(SearchEntityConfig).filter(SearchEntityConfig.entity_type == entity_type).first()
        if existing:
            raise HTTPException(status_code=400, detail="Entity type already exists")
        
        config = SearchEntityConfig(
            entity_type=entity_type, 
            base_url_route=base_url_route, 
            icon_name=icon_name
        )
        db.add(config)
        db.commit()
        db.refresh(config)
        return config

    @staticmethod
    def update_config(db: Session, entity_type: str, base_url_route: Optional[str] = None, icon_name: Optional[str] = None):
        config = db.query(SearchEntityConfig).filter(SearchEntityConfig.entity_type == entity_type).first()
        if not config:
            raise HTTPException(status_code=404, detail="Entity type not found")
        
        if base_url_route is not None:
            config.base_url_route = base_url_route
        if icon_name is not None:
            config.icon_name = icon_name
        
        db.commit()
        db.refresh(config)
        return config

    @staticmethod
    def delete_config(db: Session, entity_type: str):
        config = db.query(SearchEntityConfig).filter(SearchEntityConfig.entity_type == entity_type).first()
        if not config:
            raise HTTPException(status_code=404, detail="Entity type not found")
        
        db.delete(config)
        db.commit()
        return True
