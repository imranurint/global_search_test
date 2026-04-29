from elasticsearch import Elasticsearch
from fastapi import HTTPException
from app.core.config import settings
from typing import List, Optional

es = Elasticsearch(settings.ELASTICSEARCH_URL)
CONFIG_INDEX = "search_configs"

class ConfigService:
    @staticmethod
    def get_all_configs():
        """Fetch all entity configurations from Elasticsearch."""
        res = es.search(index=CONFIG_INDEX, query={"match_all": {}}, size=100)
        return [hit["_source"] for hit in res["hits"]["hits"]]

    @staticmethod
    def create_config(entity_type: str, base_url_route: str, icon_name: Optional[str] = None):
        """Store a new configuration document in Elasticsearch."""
        doc = {
            "entity_type": entity_type,
            "base_url_route": base_url_route,
            "icon_name": icon_name or "default_icon"
        }
        # Use entity_type as ID for easy lookup
        es.index(index=CONFIG_INDEX, id=entity_type, document=doc, refresh=True)
        return doc

    @staticmethod
    def get_config(entity_type: str):
        """Lookup config by ID."""
        try:
            res = es.get(index=CONFIG_INDEX, id=entity_type)
            return res["_source"]
        except:
            return {"base_url_route": "/dashboard/{id}", "icon_name": "default"}

    @staticmethod
    def delete_config(entity_type: str):
        """Remove configuration from Elasticsearch."""
        es.delete(index=CONFIG_INDEX, id=entity_type, refresh=True)
        return True