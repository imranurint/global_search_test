from elasticsearch import Elasticsearch, helpers
from app.core.config import settings
from app.api.schemas.event_payload import EventPayload
import datetime

# Initialize the ES Client
es = Elasticsearch(settings.ELASTICSEARCH_URL)

class ElasticIndexingService:
    @staticmethod
    def upsert_entity(payload: EventPayload):
        """Indexes or updates a document in Elasticsearch."""
        doc = {
            "entity_type": payload.entity_type,
            "entity_id": str(payload.entity_id),
            "title": payload.title,
            "subtitle": payload.subtitle,
            "status": payload.status,
            "company_ids": payload.company_ids or ([payload.company_id] if payload.company_id else []),
            "allowed_branch_ids": payload.allowed_branch_ids or [],
            "search_text": payload.search_text,
            "updated_at": datetime.datetime.utcnow().isoformat()
        }
        
        # ID is formatted to prevent collisions between different entity types
        doc_id = f"{payload.entity_type}_{payload.entity_id}"
        
        return es.index(
            index=settings.ELASTICSEARCH_INDEX, 
            id=doc_id, 
            document=doc
        )

    @staticmethod
    def delete_entity(entity_type: str, entity_id: str):
        """Removes a document from Elasticsearch."""
        try:
            doc_id = f"{entity_type}_{entity_id}"
            return es.delete(index=settings.ELASTICSEARCH_INDEX, id=doc_id)
        except Exception as e:
            # Silently fail if document doesn't exist
            print(f"ES Delete Warning: {e}")
            return None