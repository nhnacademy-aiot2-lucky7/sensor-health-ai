import pika
from config.settings import RABBITMQ


def publish_alert_message(message: str):
    """
    RabbitMQ에 알림 메시지를 발행합니다.
    """
    credentials = pika.PlainCredentials(RABBITMQ["username"], RABBITMQ["password"])
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ["host"],
            port=RABBITMQ["port"],
            credentials=credentials
        )
    )
    channel = connection.channel()

    # 큐 선언 (idempotent)
    channel.queue_declare(queue=RABBITMQ["queue"], durable=True)

    # 메시지 전송
    channel.basic_publish(
        exchange='',
        routing_key=RABBITMQ["queue"],
        body=message.encode('utf-8'),
        properties=pika.BasicProperties(delivery_mode=2)  # 메시지 영속성
    )

    print(f"✅ RabbitMQ로 알림 발송 완료: {message}")
    connection.close()