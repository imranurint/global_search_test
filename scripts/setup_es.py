from elasticsearch import Elasticsearch
from app.core.config import settings

es = Elasticsearch(settings.ELASTICSEARCH_URL)

def setup_indices():
    # 1. Configuration Index (Small)
    if not es.indices.exists(index="search_configs"):
        es.indices.create(index="search_configs")
        print("Created index: search_configs")

    # 2. Main Search Index (3.5M Records)
    # We define 'Mappings' to tell ES how to handle the data
    index_name = settings.ELASTICSEARCH_INDEX
    if not es.indices.exists(index=index_name):
        mappings = {
            "properties": {
                "entity_type": {"type": "keyword"}, # Fast filtering
                "entity_id":   {"type": "keyword"},
                "title":       {"type": "text", "analyzer": "english"}, # For search
                "subtitle":    {"type": "text", "analyzer": "english"},
                "status":      {"type": "keyword"},
                "company_ids": {"type": "integer"}, # Array of IDs
                "allowed_branch_ids": {"type": "integer"},
                "search_text": {"type": "text"},
                "updated_at":  {"type": "date"}
            }
        }
        es.indices.create(index=index_name, mappings=mappings)
        print(f"Created index: {index_name} with strict mappings.")

if __name__ == "__main__":
    setup_indices()