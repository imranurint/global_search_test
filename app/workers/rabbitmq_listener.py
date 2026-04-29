import json
import pika
from app.db.database import SessionLocal
from mieSEARCH.app.api.services.pg.indexing_service import IndexingService
from app.api.schemas.event_payload import EventPayload
from app.core.config import settings

def start_worker():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.RABBITMQ_HOST)
        )
        channel = connection.channel()
        channel.queue_declare(queue=settings.RABBITMQ_QUEUE, durable=True)

        def callback(ch, method, properties, body):
            db = SessionLocal()
            try:
                data = json.loads(body)
                payload = EventPayload(**data)
                
                if payload.event_action == "DELETE":
                    IndexingService.delete_entity(db, payload.entity_type, payload.entity_id)
                else:
                    IndexingService.upsert_entity(db, payload)
                    
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                db.rollback()
                print(f"Error processing search event: {e}")
                # Optional: nack without requeue if data is malformed
                # ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            finally:
                db.close()

        print(f" [*] Search Indexer listening on {settings.RABBITMQ_HOST}:{settings.RABBITMQ_QUEUE}")
        channel.basic_consume(queue=settings.RABBITMQ_QUEUE, on_message_callback=callback)
        channel.start_consuming()
    except Exception as e:
        print(f"RabbitMQ Worker failed to start: {e}")

if __name__ == "__main__":
    start_worker()
