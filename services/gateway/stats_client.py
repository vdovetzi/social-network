import grpc
from proto import statistics_pb2, statistics_pb2_grpc

class StatisticsClient:
    def __init__(self, url):
        self.channel = grpc.insecure_channel(url)
        self.stub = statistics_pb2_grpc.StatisticsServiceStub(self.channel)

    def get_post_stats(self, post_id: str):
        request = statistics_pb2.PostRequest(post_id=post_id)
        return self.stub.GetPostStats(request)

    def get_views_dynamic(self, post_id: str):
        request = statistics_pb2.PostRequest(post_id=post_id)
        return self.stub.GetViewsDynamic(request)

    def get_likes_dynamic(self, post_id: str):
        request = statistics_pb2.PostRequest(post_id=post_id)
        return self.stub.GetLikesDynamic(request)

    def get_comments_dynamic(self, post_id: str):
        request = statistics_pb2.PostRequest(post_id=post_id)
        return self.stub.GetCommentsDynamic(request)

    def get_top_posts(self, metric: int):
        request = statistics_pb2.TopRequest(metric=metric)
        return self.stub.GetTopPosts(request)

    def get_top_users(self, metric: int):
        request = statistics_pb2.TopRequest(metric=metric)
        return self.stub.GetTopUsers(request)
