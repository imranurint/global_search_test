from fastapi import APIRouter
from app.api.router.v1.search_router import router as search_router
from app.api.router.v1.es_search_router import router as es_search_router

api_v1_router = APIRouter()

# Register sub-routers
api_v1_router.include_router(search_router,prefix="/ps", tags=["Postgres Search"])
api_v1_router.include_router(es_search_router, prefix="/es", tags=["Elasticsearch Search"])    
