import sys
import os
from elasticsearch import Elasticsearch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings

# Initialize ES Client with meta_header disabled to fix the Compatibility Error
es = Elasticsearch(
    [settings.ELASTICSEARCH_URL],
    verify_certs=False,
    request_timeout=30,
    meta_header=False
)

INDEX_NAME = "search_configs"

def seed_search_configs():
    print(f"Connecting to Elasticsearch at {settings.ELASTICSEARCH_URL}...")
    try:
        # 1. Existence Check
        if not es.indices.exists(index=INDEX_NAME):
            es.indices.create(index=INDEX_NAME)
            print(f"Success: Created index '{INDEX_NAME}'")
        else:
            print(f"Notice: Index '{INDEX_NAME}' already exists")

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

        # 3. Seeding Loop
        for data in configs:
            es.index(index=INDEX_NAME, id=data["entity_type"], document=data, refresh=True)
            print(f" -> Indexing complete for: {data['entity_type']}")
            
        print("\n--- ES Seeding Completed Successfully ---")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    seed_search_configs()