import sys
import os

# Add project root to path so we can import 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import SessionLocal
from app.models.entity_config import SearchEntityConfig

def seed_search_configs():
    db = SessionLocal()
    
    # Data based on your CRM structure
    configs = [
        {"entity_type": "lead", "base_url_route": "/crm/leads/{id}", "icon_name": "PersonOutline", "display_priority": 1},
        {"entity_type": "applicant", "base_url_route": "/crm/applicants/{id}", "icon_name": "School", "display_priority": 2},
        {"entity_type": "application", "base_url_route": "/crm/applications/{id}", "icon_name": "Assignment", "display_priority": 3},
        {"entity_type": "university", "base_url_route": "/crm/universities/{id}", "icon_name": "AccountBalance", "display_priority": 4},
        {"entity_type": "course", "base_url_route": "/crm/courses/{id}", "icon_name": "MenuBook", "display_priority": 5},
        {"entity_type": "partner", "base_url_route": "/partners/list/{id}", "icon_name": "Handshake", "display_priority": 6},
    ]

    try:
        for data in configs:
            # Check if this type already exists
            existing = db.query(SearchEntityConfig).filter_by(entity_type=data["entity_type"]).first()
            if not existing:
                new_cfg = SearchEntityConfig(**data)
                db.add(new_cfg)
                print(f"Added: {data['entity_type']}")
            else:
                # Update existing if route changed
                existing.base_url_route = data["base_url_route"]
                existing.icon_name = data["icon_name"]
                print(f"Updated: {data['entity_type']}")
        
        db.commit()
        print("\n--- Seeding Completed Successfully ---")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_search_configs()