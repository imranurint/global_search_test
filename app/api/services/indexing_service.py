from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.search_index import GlobalSearchIndex
from app.api.schemas.event_payload import EventPayload

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
        else:
            # UPDATE the entity_type if it changed in the CRM
            # e.g., from 'lead' to 'applicant'
            record.entity_type = payload.entity_type

        record.title = payload.title
        record.subtitle = payload.subtitle
        record.status = payload.status
        
        # Security logic in IndexingService
        if payload.company_ids:
            record.company_ids = payload.company_ids
        elif payload.company_id:
            record.company_ids = [payload.company_id]
        else:
            # Entities with no company become "Global"
            record.company_ids = None

        record.allowed_branch_ids = payload.allowed_branch_ids
        
        # Senior Engineering approach: Weighted Full-Text Search
        # Title (A) = 1.0 rank | Subtitle (B) = 0.4 rank | Search Text (C) = 0.2 rank
        # This ensures a name match appears higher than a detail match.
        record.search_vector = (
            func.setweight(func.to_tsvector('english', payload.title or ''), 'A').op('||')(
                func.setweight(func.to_tsvector('english', payload.subtitle or ''), 'B').op('||')(
                    func.setweight(func.to_tsvector('english', payload.search_text or ''), 'C')
                )
            )
        )

        db.commit()

    @staticmethod
    def delete_entity(db: Session, entity_type: str, entity_id: str):
        db.query(GlobalSearchIndex).filter(
            GlobalSearchIndex.entity_type == entity_type,
            GlobalSearchIndex.entity_id == entity_id
        ).delete()
        db.commit()
