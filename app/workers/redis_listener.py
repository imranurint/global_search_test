import json
import redis
import time
from app.db.database import SessionLocal
from mieSEARCH.app.api.services.pg.indexing_service import IndexingService
from app.api.schemas.event_payload import EventPayload
from app.core.config import settings

def start_redis_worker():
    # 1. Connection setup
    r = redis.Redis(
        host=settings.REDIS_HOST, 
        port=settings.REDIS_PORT, 
        decode_responses=True
    )
    
    stream_key = "search_events_stream"
    group_name = "search_indexer_group"
    consumer_name = "worker_1"

    # 2. Create Consumer Group (if it doesn't exist)
    # mkstream=True creates the stream automatically if it's missing
    try:
        r.xgroup_create(stream_key, group_name, id='0', mkstream=True)
    except redis.exceptions.ResponseError as e:
        if "already exists" not in str(e):
            raise e

    print(f" [*] Search Indexer listening on Redis Stream: {stream_key}")

    while True:
        try:
            # 3. Read from Group ('>' means read new messages never delivered to others)
            # block=0 means wait indefinitely for a new message
            messages = r.xreadgroup(group_name, consumer_name, {stream_key: '>'}, count=1, block=0)

            for _, message_list in messages:
                for message_id, data in message_list:
                    db = SessionLocal()
                    try:
                        # Extract and parse the JSON payload
                        payload_data = json.loads(data['payload'])
                        payload = EventPayload(**payload_data)

                        # 4. Processing logic (identical to RabbitMQ logic)
                        if payload.event_action == "DELETE":
                            IndexingService.delete_entity(db, payload.entity_type, payload.entity_id)
                        else:
                            IndexingService.upsert_entity(db, payload)

                        # 5. Acknowledge (Tells Redis I finished processing this message)
                        r.xack(stream_key, group_name, message_id)
                        
                    except Exception as e:
                        db.rollback()
                        print(f"Error processing message {message_id}: {e}")
                    finally:
                        db.close()
                        
        except Exception as e:
            print(f"Redis Worker Connection Error: {e}")
            time.sleep(5)  # Wait before retrying connection

if __name__ == "__main__":
    start_redis_worker()