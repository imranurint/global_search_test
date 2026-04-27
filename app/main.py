from fastapi import FastAPI
from app.api.router.v1 import api_v1_router
from app.db.database import engine
from app.db.base import Base
import threading
from app.workers.rabbitmq_listener import start_worker

# Initialize DB tables - COMMENTED OUT FOR ALEMBIC
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="mieSEARCH Service")

app.include_router(api_v1_router, prefix="/api/v1")

@app.on_event("startup")
def startup_event():
    # Start RabbitMQ worker in a background thread
    worker_thread = threading.Thread(target=start_worker, daemon=True)
    worker_thread.start()

@app.get("/health")
def health_check():
    return {"status": "healthy"}
