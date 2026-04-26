from fastapi import APIRouter
from app.api.v1.search_router import router as search_router

api_v1_router = APIRouter()

# Register sub-routers
api_v1_router.include_router(search_router)
