import os
import time
import json
import logging
import signal
from datetime import datetime
from celery.result import AsyncResult
from worker import get_github_data, app 
from rb_queue.rabbitmq import get_connection, QUEUE_NAME
from pydantic_models.github import RabbitMQ_Data_Validation
from pydantic import ValidationError


celery_task_get_repos = get_github_data.delay()
result = AsyncResult(celery_task_get_repos.id, app=app)


print("Waiting for Celery task to complete")

# Collection to store all repository data from RabbitMQ
collected_repos = []

def consume_all_messages():
    """Consume all messages currently in the RabbitMQ queue"""
    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    
    # Get the number of messages in the queue
    method_frame = channel.queue_declare(queue=QUEUE_NAME, durable=True, passive=True)
    message_count = method_frame.method.message_count
    print(f"Found {message_count} messages in queue")
    
    messages_consumed = 0
    
    try:
        # Consume messages one at a time until queue is empty
        while True:
            method_frame, header_frame, body = channel.basic_get(queue=QUEUE_NAME)
            
            if method_frame is None:
                # No more messages
                print("No more messages in queue")
                break
            
            try:
                repo = RabbitMQ_Data_Validation.model_validate_json(body)
                print(f"Received data from RMQ: {repo.name}")
                # Convert Pydantic model to dict for JSON serialization
                collected_repos.append(repo.model_dump())
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                messages_consumed += 1
            except ValidationError as e:
                print(f"Validation Error: {e}")
                channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=False)
                
    except Exception as e:
        print(f"Error consuming messages: {e}")
    finally:
        connection.close()
        print(f"Consumed {messages_consumed} messages")

def save_data_to_file():
    """Save collected data to JSON file in the mounted volume"""
    # Ensure the data directory exists (persisted via Docker volume)
    os.makedirs("data", exist_ok=True)
    
    # Save collected data to JSON file in the mounted volume
    data_file_path = "data/gh_data.json"
    with open(data_file_path, mode="w") as f:
        json.dump(collected_repos, f, default=str, indent=2)
    
    print(f"Saved {len(collected_repos)} repositories to {data_file_path}")

while True:
    if result.ready():
        try:
            print('Getting the result')
            result.get()
        except Exception as e:
            print(e)
            break
        else:
            print('Done. The result state of the queue', result.state)

            # Consume all messages from RabbitMQ
            consume_all_messages()
            
            # Save data to file
            save_data_to_file()
            break
    else:
        print("Results are not ready")
        print(result.state)
        time.sleep(1)