from elasticsearch import Elasticsearch
from typing import List, Dict, Optional
from app.core.config import settings
from app.api.schemas.search_response import SearchResultResponse
from app.api.schemas.sectioned_response import SectionedSearchResponse

# Initialize the Elasticsearch Client
es = Elasticsearch(settings.ELASTICSEARCH_URL)

class ElasticSearchService:
    @classmethod
    def execute_search(
        cls, 
        q: str, 
        company_id: int, 
        branch_ids: Optional[List[int]] = None,
        entity_types: Optional[List[str]] = None,
        size: int = 20,
        from_: int = 0
    ) -> SectionedSearchResponse:
        """
        Executes a high-efficiency fuzzy search across 3M records in Elasticsearch.
        Replaces PostgreSQL weighted full-text search.
        """
        
        # 1. Build the Search Query with Weighting (Title is most important)
        query = {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": q,
                            "fields": ["title^3", "subtitle^2", "search_text"],
                            "fuzziness": "AUTO",  # Handles typos automatically
                            "operator": "and"     # Ensures higher precision
                        }
                    }
                ],
                "filter": [
                    {
                        "bool": {
                            "should": [
                                # Security: Only see records for your company
                                {"terms": {"company_ids": [company_id]}},
                                # Global records: Some entities are visible to everyone
                                {"terms": {"entity_type": ['university', 'course', 'partner']}},
                                # Records with no assigned company (Global)
                                {"bool": {"must_not": {"exists": {"field": "company_ids"}}}}
                            ]
                        }
                    }
                ]
            }
        }

        # Add Entity Type Filter
        if entity_types:
            query["bool"]["filter"].append({"terms": {"entity_type": entity_types}})

        # 2. Apply Branch-level security if branch_ids are provided
        if branch_ids:
            query["bool"]["filter"].append({
                "bool": {
                    "should": [
                        {"terms": {"allowed_branch_ids": branch_ids}},
                        {"bool": {"must_not": {"exists": {"field": "allowed_branch_ids"}}}}
                    ]
                }
            })

        # 3. Execute Search with from/size for pagination
        response = es.search(
            index=settings.ELASTICSEARCH_INDEX,
            query=query,
            from_=from_,  # Starting point
            size=size    # Number of results
        )

        # --- EXPLANATION START ---
        # 1. We fetch all icons/routes from our Config Index (Replacing PostgreSQL Table)
        # Result looks like: {"lead": {"icon_name": "person", "base_url_route": "/crm/leads/{id}"}, ...}
        from app.api.services.es.elastic_config_service import ConfigService
        all_configs = {c['entity_type']: c for c in ConfigService.get_all_configs()}
        
        sections = {}
        total = response['hits']['total']['value']

        for hit in response['hits']['hits']:
            source = hit['_source']
            etype = source['entity_type']
            
            # 2. We look up the settings for THIS entity type (e.g., 'lead')
            # If we don't find it in our configs, we use a 'bolt' icon as fallback.
            cfg = all_configs.get(etype, {"base_url_route": "/dashboard/{id}", "icon_name": "bolt"})
            
            # 3. We create the response object using the correct Icon and URL from our configs
            item = SearchResultResponse(
                id=hit['_id'],
                entity_type=etype,
                entity_id=source['entity_id'],
                title=source['title'],
                subtitle=source['subtitle'],
                status=source['status'],
                # We replace {id} in the route string with the actual ID (e.g., /crm/leads/55)
                routing_url=cfg["base_url_route"].format(id=source['entity_id']),
                icon_name=cfg["icon_name"]
            )
            # --- EXPLANATION END ---

            # Group into sections (Lead, Applicant, etc.)
            section_name = etype.capitalize()
            if section_name not in sections:
                sections[section_name] = []
            sections[section_name].append(item)

        return SectionedSearchResponse(
            total_count=total,
            sections=sections
        )

    @classmethod
    def get_data_by_type(
        cls, 
        entity_type: str, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[SearchResultResponse]:
        """
        Fetch latest records for a specific type (e.g., for Recent Leads list).
        Replaces the old 'get_indexed_data_by_type' PostgreSQL method.
        """
        query = {
            "term": { "entity_type": entity_type }
        }

        response = es.search(
            index=settings.ELASTICSEARCH_INDEX,
            query=query,
            from_=offset,
            size=limit,
            sort=[{"updated_at": {"order": "desc"}}]
        )

        output = []
        for hit in response['hits']['hits']:
            source = hit['_source']
            output.append(SearchResultResponse(
                id=hit['_id'],
                entity_type=source['entity_type'],
                entity_id=source['entity_id'],
                title=source['title'],
                subtitle=source['subtitle'],
                status=source['status'],
                routing_url=f"/dashboard/{source['entity_type']}/{source['entity_id']}",
                icon_name="default"
            ))
        return output