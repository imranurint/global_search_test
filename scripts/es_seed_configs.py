import sys
import os
from elasticsearch import Elasticsearch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings

# FIX: Add more robust initialization
es = Elasticsearch(
    [settings.ELASTICSEARCH_URL],
    verify_certs=False,
    request_timeout=30
)
INDEX_NAME = "search_configs"

def seed_search_configs():
    try:
        # Check if index exists - using the proper ES8 syntax
        exists = es.indices.exists(index=INDEX_NAME)
        
        if not exists:
            # Explicitly create index with an empty body to avoid 400 error
            es.indices.create(index=INDEX_NAME)
            print(f"Created index: {INDEX_NAME}")

    except Exception as e:
        print(f"Error checking index existence: {e}")

    # 2. Data to seed
    configs = [
        {"entity_type": "lead", "base_url_route": "/crm/leads/{id}", "icon_name": "PersonOutline", "display_priority": 1},
        {"entity_type": "applicant", "base_url_route": "/crm/applicants/{id}", "icon_name": "School", "display_priority": 2},
        {"entity_type": "application", "base_url_route": "/crm/applications/{id}", "icon_name": "Assignment", "display_priority": 3},
        {"entity_type": "university", "base_url_route": "/crm/universities/{id}", "icon_name": "AccountBalance", "display_priority": 4},
        {"entity_type": "course", "base_url_route": "/crm/courses/{id}", "icon_name": "MenuBook", "display_priority": 5},
        {"entity_type": "partner", "base_url_route": "/partners/list/{id}", "icon_name": "Handshake", "display_priority": 6},
        {"entity_type": "user", "base_url_route": "/settings/users/{id}", "icon_name": "People", "display_priority": 9},
    ]

    print(f"Seeding {len(configs)} configurations into Elasticsearch...")

    try:
        for data in configs:
            # We use entity_type as the Document ID so we can easily update/get it
            doc_id = data["entity_type"]
            
            es.index(
                index=INDEX_NAME,
                id=doc_id,
                document=data,
                refresh=True # Ensures data is searchable immediately
            )
            print(f"Indexed: {doc_id}")
            
        print("\n--- ES Seeding Completed Successfully ---")
    except Exception as e:
        print(f"Error seeding ES: {e}")

if __name__ == "__main__":
    seed_search_configs()