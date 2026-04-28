import redis
import json
import time

def send_test_stream_event(payload):
    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    stream_key = 'search_events_stream'
    
    # In Redis Streams, data is stored as key-value pairs. 
    # We wrap our JSON in a field called 'payload' to match the worker.
    message_data = {
        "payload": json.dumps(payload)
    }
    
    # XADD adds a message to the stream
    # '*' tells Redis to autogenerate a unique Message ID
    message_id = r.xadd(stream_key, message_data)
    
    print(f" [x] Sent to Stream: {payload['event_action']} | ID: {message_id}")

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
    send_test_stream_event(create_payload)
    time.sleep(1)

    # 2. TEST: Update that Lead
    update_payload = create_payload.copy()
    update_payload["event_action"] = "UPDATE"
    update_payload["status"] = "Converted"
    send_test_stream_event(update_payload)
    time.sleep(1)

    # 3. TEST: Delete that Lead
    delete_payload = {
        "event_action": "DELETE",
        "entity_type": "lead",
        "entity_id": "101"
    }
    # send_test_stream_event(delete_payload)