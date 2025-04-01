from proto import service_pb2, service_pb2_grpc
from datetime import datetime
from google.protobuf.json_format import MessageToDict
from google.protobuf.timestamp_pb2 import Timestamp
import grpc
import logging



class PostServiceClient:
    def __init__(self, api_url):
        self.channel = grpc.insecure_channel(api_url, options=(('grpc.enable_http_proxy', 0), ('grpc.client_timeout', 5000)))
        self.stub = service_pb2_grpc.PostServiceStub(self.channel)
    
    def create_post(self, data):
        try:
            request = service_pb2.CreatePostRequest(
                title=data['title'],
                description=data.get('description', ''),
                creator_id=data['creator_id'],
                is_private=data.get('is_private', False),
                tags=data.get('tags', [])
            )
            response = self.stub.CreatePost(request)
            return MessageToDict(response.post)
        except grpc.RpcError as e:
            logging.error(f"gRPC error: {e.code()}: {e.details()}")
            raise
    
    def get_post(self, post_id, user_id):
        try:
            request = service_pb2.GetPostRequest(
                id=post_id,
                user_id=user_id
            )
            response = self.stub.GetPost(request)
            logging.error(f"Is Private: {response.is_private}")
            return MessageToDict(response.post)
        except grpc.RpcError as e:
            logging.error(f"gRPC error: {e.code()}: {e.details()}")
            raise
    
    def update_post(self, post_id, data):
        try:
            request = service_pb2.UpdatePostRequest(
                id=post_id,
                title=data.get('title'),
                description=data.get('description'),
                updater_id=data['updater_id'],
                is_private=data.get('is_private'),
                tags=data.get('tags', [])
            )
            response = self.stub.UpdatePost(request)
            return MessageToDict(response.post)
        except grpc.RpcError as e:
            logging.error(f"gRPC error: {e.code()}: {e.details()}")
            raise
    
    def delete_post(self, post_id, deleter_id):
        try:
            request = service_pb2.DeletePostRequest(
                id=post_id,
                deleter_id=deleter_id
            )
            response = self.stub.DeletePost(request)
            return {'success': response.success}
        except grpc.RpcError as e:
            logging.error(f"gRPC error: {e.code()}: {e.details()}")
            raise
    
    def list_posts(self, page, per_page, user_id):
        try:
            request = service_pb2.ListPostsRequest(
                page=page,
                per_page=per_page,
                user_id=user_id
            )
            response = self.stub.ListPosts(request)
            return {
                'posts': [MessageToDict(post) for post in response.posts],
                'total': response.total,
                'page': response.page,
                'per_page': response.per_page
            }
        except grpc.RpcError as e:
            logging.error(f"gRPC error: {e.code()}: {e.details()}")
            raise