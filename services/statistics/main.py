from concurrent import futures
import grpc
import clickhouse_driver
from kafka import KafkaConsumer
import json
import threading
import statistics_pb2
import statistics_pb2_grpc
import os
import logging
import time
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(threadName)s %(message)s'
)

client = clickhouse_driver.Client(
        host='clickhouse',
        user=os.getenv("CLICKHOUSE_USER"),
        port=9000,
        password=os.getenv("CLICKHOUSE_PASSWORD")
)


class StatisticsService(statistics_pb2_grpc.StatisticsServiceServicer):
    def __init__(self):
        pass

    def GetPostStats(self, request, context):
        views = client.execute(
            "SELECT count() FROM statistics.post_views WHERE post_id = %(post_id)s",
            {'post_id': request.post_id}
        )[0][0]

        likes = client.execute(
            "SELECT count() FROM statistics.post_likes WHERE post_id = %(post_id)s AND is_like = 1",
            {'post_id': request.post_id}
        )[0][0]

        comments = client.execute(
            "SELECT count() FROM statistics.post_comments WHERE post_id = %(post_id)s",
            {'post_id': request.post_id}
        )[0][0]

        return statistics_pb2.PostStatsResponse(
            views=views,
            likes=likes,
            comments=comments
        )

    def GetViewsDynamic(self, request, context):
        data = client.execute(
            """
            SELECT toDate(view_date) as day, count() as views
            FROM statistics.post_views
            WHERE post_id = %(post_id)s
            GROUP BY day
            ORDER BY day
            """,
            {'post_id': request.post_id}
        )
        return statistics_pb2.DynamicResponse(
            data=[statistics_pb2.DynamicData(date=str(day), count=int(count)) for day, count in data]
        )

    def GetLikesDynamic(self, request, context):
        data = client.execute(
            """
            SELECT toDate(like_date) as day, count() as likes
            FROM statistics.post_likes
            WHERE post_id = %(post_id)s AND is_like = 1
            GROUP BY day
            ORDER BY day
            """,
            {'post_id': request.post_id}
        )
        return statistics_pb2.DynamicResponse(
            data=[statistics_pb2.DynamicData(date=str(day), count=int(count)) for day, count in data]
        )

    def GetCommentsDynamic(self, request, context):
        data = client.execute(
            """
            SELECT toDate(comment_date) as day, count() as comments
            FROM statistics.post_comments
            WHERE post_id = %(post_id)s
            GROUP BY day
            ORDER BY day
            """,
            {'post_id': request.post_id}
        )
        return statistics_pb2.DynamicResponse(
            data=[statistics_pb2.DynamicData(date=str(day), count=int(count)) for day, count in data]
        )

    def GetTopPosts(self, request, context):
        if request.metric == statistics_pb2.Metric.VIEWS:
            query = """
                SELECT post_id, count() as count
                FROM statistics.post_views
                GROUP BY post_id
                ORDER BY count DESC
                LIMIT 10
            """
        elif request.metric == statistics_pb2.Metric.LIKES:
            query = """
                SELECT post_id, count() as count
                FROM statistics.post_likes
                WHERE is_like = 1
                GROUP BY post_id
                ORDER BY count DESC
                LIMIT 10
            """
        else:  # COMMENTS
            query = """
                SELECT post_id, count() as count
                FROM statistics.post_comments
                GROUP BY post_id
                ORDER BY count DESC
                LIMIT 10
            """

        data = client.execute(query)
        return statistics_pb2.TopPostsResponse(
            posts = [
                statistics_pb2.TopPost(post_id=str(post_id), count=int(count))
                for post_id, count in data
            ]
        )

    def GetTopUsers(self, request, context):
        if request.metric == statistics_pb2.Metric.VIEWS:
            query = """
                SELECT user_id, count() as count
                FROM statistics.post_views
                GROUP BY user_id
                ORDER BY count DESC
                LIMIT 10
            """
        elif request.metric == statistics_pb2.Metric.LIKES:
            query = """
                SELECT user_id, count() as count
                FROM statistics.post_likes
                WHERE is_like = 1
                GROUP BY user_id
                ORDER BY count DESC
                LIMIT 10
            """
        else:  # COMMENTS
            query = """
                SELECT user_id, count() as count
                FROM statistics.post_comments
                GROUP BY user_id
                ORDER BY count DESC
                LIMIT 10
            """

        data = client.execute(query)
        return statistics_pb2.TopUsersResponse(
            users =[
                statistics_pb2.TopUser(user_id=str(user_id), count=int(count))
                for user_id, count in data
            ]           
        )


topics_groups = {
    'posts_views': 'views-group',
    'posts_likes': 'likes-group',
    'posts_comments': 'comments-group',
}

def consume_topic(topic, group_id, client):
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers='kafka:29092',
        group_id=group_id,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    logging.info(f"Started consumer for topic: {topic}, group: {group_id}")

    while True:
        try:
            for message in consumer:
                data = message.value
                logging.info(f"[{topic}] Consumed: {data}")

                timestamp_str = data['timestamp'].replace('Z', '')
                timestamp = datetime.fromisoformat(timestamp_str)

                if topic == 'posts_views':
                    client.execute(
                        "INSERT INTO statistics.post_views (post_id, user_id, view_date, view_time) VALUES",
                        [{
                            'post_id': data['entity_id'],
                            'user_id': data['client_id'],
                            'view_date': timestamp.date(),
                            'view_time': timestamp
                        }]
                    )
                elif topic == 'posts_likes':
                    client.execute(
                        "INSERT INTO statistics.post_likes (post_id, user_id, like_date, like_time, is_like) VALUES",
                        [{
                            'post_id': data['entity_id'],
                            'user_id': data['client_id'],
                            'like_date': timestamp.date(),
                            'like_time': timestamp,
                            'is_like': data.get('is_like', 1)
                        }]
                    )
                elif topic == 'posts_comments':
                    client.execute(
                        "INSERT INTO statistics.post_comments (post_id, user_id, comment_id, comment_date, comment_time) VALUES",
                        [{
                            'post_id': data['post_id'],
                            'user_id': data['client_id'],
                            'comment_id': data['comment_id'],
                            'comment_date': timestamp.date(),
                            'comment_time': timestamp
                        }]
                    )
        except Exception as e:
            logging.error(f"Error in topic {topic} consumer: {e}")

def consume_kafka_messages():
    for topic, group in topics_groups.items():
        t = threading.Thread(target=consume_topic, args=(topic, group, client), daemon=True)
        t.start()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    statistics_pb2_grpc.add_StatisticsServiceServicer_to_server(
        StatisticsService(), server)
    server.add_insecure_port('[::]:8092')
    server.start()

    logging.info("Starting Kafka consumer thread...")
    
    consume_kafka_messages()
    
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
