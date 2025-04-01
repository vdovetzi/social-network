import grpc
from concurrent import futures
from ..proto import service_pb2, service_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime
from typing import Dict, List
import logging
from uuid import uuid4

logging.basicConfig(level=logging.INFO)

class Post:
    def __init__(self, id: str, title: str, description: str, creator_id: str, 
                 is_private: bool, tags: List[str]):
        self.id = id
        self.title = title
        self.description = description
        self.creator_id = creator_id
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.is_private = is_private
        self.tags = tags

class PostServiceImpl(service_pb2_grpc.PostServiceServicer):
    def __init__(self):
        self.posts: Dict[str, Post] = {}
        self.initialize_sample_data()
    
    def initialize_sample_data(self):
        """Initialize with some sample posts"""
        sample_posts = [
            Post(
                id=str(uuid4()),
                title="First Post",
                description="This is my first post",
                creator_id="user1",
                is_private=False,
                tags=["welcome", "first"]
            ),
            Post(
                id=str(uuid4()),
                title="Private Thoughts",
                description="My private thoughts",
                creator_id="user1",
                is_private=True,
                tags=["personal"]
            ),
            Post(
                id=str(uuid4()),
                title="Public Announcement",
                description="Important announcement for everyone",
                creator_id="user2",
                is_private=False,
                tags=["announcement", "important"]
            )
        ]
        for post in sample_posts:
            self.posts[post.id] = post
    
    def CreatePost(self, request, context):
        """Create a new post"""
        try:
            post_id = str(uuid4())
            new_post = Post(
                id=post_id,
                title=request.title,
                description=request.description,
                creator_id=request.creator_id,
                is_private=request.is_private,
                tags=list(request.tags)
            )
            
            self.posts[post_id] = new_post

            logging.info(f"{new_post.is_private}")
            
            return service_pb2.PostResponse(
                post=self._post_to_proto(new_post)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error creating post: {str(e)}")
            return service_pb2.PostResponse()
    
    def GetPost(self, request, context):
        """Get a post by ID with permission check"""
        try:
            post = self.posts.get(request.id)
            if not post:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Post not found")
                return service_pb2.PostResponse()
            
            return service_pb2.PostResponse(
                post=self._post_to_proto(post)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting post: {str(e)}")
            return service_pb2.PostResponse()
    
    def UpdatePost(self, request, context):
        """Implementation of UpdatePost RPC method"""
        try:
            post = self.posts.get(request.id)
            if not post:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Post not found")
                return service_pb2.PostResponse()
            
            if post.creator_id != request.updater_id:
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                context.set_details("Only the post creator can update the post")
                return service_pb2.PostResponse()
            
            # Update fields
            if request.title:
                post.title = request.title
            if request.description:
                post.description = request.description
            if request.HasField("is_private"):
                post.is_private = request.is_private
            if request.tags:
                post.tags = list(request.tags)
            
            post.updated_at = datetime.now()  # Update timestamp
            
            return service_pb2.PostResponse(
                post=self._post_to_proto(post)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error updating post: {str(e)}")
            return service_pb2.PostResponse()
    
    def DeletePost(self, request, context):
        """Delete a post"""
        try:
            post = self.posts.get(request.id)
            if not post:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Post not found")
                return service_pb2.DeletePostResponse(success=False)
            
            # Verify the deleter is the creator
            if post.creator_id != request.deleter_id:
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                context.set_details("Only the post creator can delete the post")
                return service_pb2.DeletePostResponse(success=False)
            
            del self.posts[request.id]
            return service_pb2.DeletePostResponse(success=True)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error deleting post: {str(e)}")
            return service_pb2.DeletePostResponse(success=False)
    
    def ListPosts(self, request, context):
        """List posts with pagination and privacy check"""
        try:
            page = max(1, request.page)
            per_page = max(1, min(request.per_page, 100))  # Limit to 100 per page
            
            # Filter posts based on privacy
            visible_posts = []
            for post in self.posts.values():
                if not post.is_private or post.creator_id == request.user_id:
                    visible_posts.append(post)
            
            # Sort by creation date (newest first)
            visible_posts.sort(key=lambda p: p.created_at, reverse=True)
            
            # Apply pagination
            total = len(visible_posts)
            start = (page - 1) * per_page
            end = start + per_page
            paginated_posts = visible_posts[start:end]
            
            return service_pb2.ListPostsResponse(
                posts=[self._post_to_proto(post) for post in paginated_posts],
                total=total,
                page=page,
                per_page=per_page
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error listing posts: {str(e)}")
            return service_pb2.ListPostsResponse()
    
    def _post_to_proto(self, post: Post) -> service_pb2.Post:
        """Convert internal Post object to protobuf Post message"""
        return service_pb2.Post(
            id=post.id,
            title=post.title,
            description=post.description,
            creator_id=post.creator_id,
            created_at=self._datetime_to_timestamp(datetime.fromisoformat(post.created_at)),
            updated_at=self._datetime_to_timestamp(datetime.fromisoformat(post.updated_at)),
            is_private=post.is_private,
            tags=post.tags
        )
    def _datetime_to_timestamp(self, dt: datetime) -> Timestamp:
        """Convert Python datetime to protobuf Timestamp"""
        timestamp = Timestamp()
        timestamp.FromDatetime(dt)
        return timestamp

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_PostServiceServicer_to_server(PostServiceImpl(), server)
    server.add_insecure_port('0.0.0.0:8091')
    server.start()
    logging.info("Posts gRPC server started on port 8091")
    
    server.wait_for_termination(timeout=None)

if __name__ == '__main__':
    serve()