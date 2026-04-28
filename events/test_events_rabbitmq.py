import pika
import json
import time

def send_test_event(payload):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # Declare the queue (must match exactly what the worker is listening to)
    channel.queue_declare(queue='global_search_updates', durable=True)

    message = json.dumps(payload)
    channel.basic_publish(
        exchange='',
        routing_key='global_search_updates',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))
    print(f" [x] Sent Event: {payload['event_action']} | {payload['entity_type']} {payload['entity_id']}")
    connection.close()

if __name__ == "__main__":
    # 1. TEST: Create a Lead
    create_payload = {
        "event_action": "CREATE",
        "entity_type": "lead",
        "entity_id": "101",
        "title": "John Doe",
        "subtitle": "Software Inquiry",
        "status": "In Progress",
        "company_ids": [1],
        "allowed_branch_ids": [10, 20],
        "search_text": "John Doe software developer interested in python"
    }
    send_test_event(create_payload)
    time.sleep(1)

    # 2. TEST: Update (Patch) that Lead
    update_payload = create_payload.copy()
    update_payload["event_action"] = "UPDATE"
    update_payload["status"] = "Converted"
    update_payload["search_text"] = "John Doe developer converted to customer"
    send_test_event(update_payload)
    time.sleep(1)

    # 3. TEST: Delete that Lead
    # For deletion, we usually only need entity_type and entity_id
    delete_payload = {
        "event_action": "DELETE",
        "entity_type": "lead",
        "entity_id": "101"
    }
    # send_test_event(delete_payload) # Uncomment this to test deletion