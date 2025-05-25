import os
import json
import logging
from datetime import datetime
from kafka import KafkaProducer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', ['kafka:29092', 'localhost:9092'])

client_topic =  os.getenv('KAFKA_TOPIC_CLIENT_REG', 'client_registrations')
like_topic =  os.getenv('KAFKA_TOPIC_LIKES', 'posts_likes')
view_topic =  os.getenv('KAFKA_TOPIC_VIEWS', 'posts_views')
comment_topic =  os.getenv('KAFKA_TOPIC_COMMENTS', 'posts_comments')

producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8') if isinstance(k, str) else None
)

logger.info(f"Initialized KafkaProducerClient with brokers {bootstrap_servers}")

def send_event(topic: str, key: str, payload: dict):
    try:
        producer.send(topic, key=key, value=payload)
        producer.flush()
        logger.info(f"Sent event to topic={topic}, key={key}")
    except Exception as e:
        logger.error(f"Failed to send event to topic={topic}, key={key}: {e}")

def send_client_registration(client_id: str, registered_at: datetime = datetime.utcnow()):
    payload = {
        'client_id': client_id,
        'registered_at': (registered_at).isoformat() + 'Z'
    }
    send_event(client_topic, client_id, payload)

def send_like_event(client_id: str, entity_id: str, liked_at: datetime = datetime.utcnow()):
    payload = {
        'client_id': client_id,
        'entity_id': entity_id,
        'action': 'like',
        'timestamp': (liked_at).isoformat() + 'Z'
    }
    send_event(like_topic, client_id, payload)

def send_view_event(client_id: str, entity_id: str, viewed_at: datetime = datetime.utcnow()):
    payload = {
        'client_id': client_id,
        'entity_id': entity_id,
        'action': 'view',
        'timestamp': (viewed_at).isoformat() + 'Z'
    }
    send_event(view_topic, client_id, payload)

def send_comment_event(client_id: str, post_id: str,  comment_id: str, commented_at: datetime = datetime.utcnow()):
    payload = {
        'client_id': client_id,
        'action': 'comment',
        'post_id': post_id,
        'comment_id': comment_id,
        'timestamp': (commented_at).isoformat() + 'Z'
    }

    send_event(comment_topic, client_id, payload)
