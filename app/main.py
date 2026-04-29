from fastapi import FastAPI
from contextlib import asynccontextmanager
import threading
from app.workers.rabbitmq_listener import start_worker

from app.api.router.v1 import api_v1_router as search_router

# 1. Define the Lifespan (This handles both Startup and Shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic: Start the RabbitMQ worker in a background thread
    print("Starting RabbitMQ Consumer...")
    worker_thread = threading.Thread(target=start_worker, daemon=True)
    worker_thread.start()
    
    yield
    
    # Shutdown logic (optional): Add cleanup here if needed
    print("Shutting down...")

# 2. Initialize FastAPI with lifespan
app = FastAPI(
    title="mieSEARCH API",
    lifespan=lifespan
)

# 3. Include Routers
app.include_router(search_router, prefix="/api/v1", tags=["Search"])

@app.get("/")
async def root():
    return {"message": "Global Search Microservice Running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
