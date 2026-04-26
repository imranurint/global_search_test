from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.search_index import GlobalSearchIndex
from app.schemas.event_payload import EventPayload

class IndexingService:
    @staticmethod
    def upsert_entity(db: Session, payload: EventPayload):
        record = db.query(GlobalSearchIndex).filter(
            GlobalSearchIndex.entity_type == payload.entity_type,
            GlobalSearchIndex.entity_id == payload.entity_id
        ).first()

        if not record:
            record = GlobalSearchIndex(
                entity_type=payload.entity_type,
                entity_id=payload.entity_id
            )
            db.add(record)

        record.title = payload.title
        record.subtitle = payload.subtitle
        record.status = payload.status
        record.company_id = payload.company_id
        record.allowed_branch_ids = payload.allowed_branch_ids
        
        if payload.search_text:
            record.search_vector = func.to_tsvector('english', payload.search_text)

        db.commit()

    @staticmethod
    def delete_entity(db: Session, entity_type: str, entity_id: str):
        db.query(GlobalSearchIndex).filter(
            GlobalSearchIndex.entity_type == entity_type,
            GlobalSearchIndex.entity_id == entity_id
        ).delete()
        db.commit()
