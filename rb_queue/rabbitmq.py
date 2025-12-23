import os
import pika 
from models.github import RabbitMQ_Data_Validation


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
QUEUE_NAME = "github_repos"

def get_conection():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    return pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST, 
            port=5672,
            credentials=credentials
        )
    )


def consume_repos(callback):
    connection = get_conection()
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    def on_message(ch, method, properties, body):
        repo = RabbitMQ_Data_Validation.model_validate_json(body)
        callback(repo)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=on_message)
    channel.start_consuming()


def publish_repo(repo_data: dict):
    repo = RabbitMQ_Data_Validation(**repo_data)
    connection = get_conection()
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=QUEUE_NAME,
        body=repo.model_dump_json(),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()