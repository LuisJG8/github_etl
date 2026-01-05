import os
import pika
import time 
from pydantic import ValidationError
from pydantic_models.github import RabbitMQ_Data_Validation


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
QUEUE_NAME = "github_repos"


def get_connection():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    
    return pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST, 
            port=5672,
            credentials=credentials
        )
    )


def consume_repos(callback):
    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    # properties is needed becayse channel.basic_consume expects 4 parameters, properties does not have
    # any value but it is required to meet the 4 parameters requirement
    def on_message(ch, method, properties, body):
        try:
            repo = RabbitMQ_Data_Validation.model_validate_json(body)
            callback(repo)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except ValidationError as e:
            print(f"Validation Error: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=on_message)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    finally:
        connection.close()