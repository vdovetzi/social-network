import grpc
from concurrent import futures
from ..proto import service_pb2, service_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime
from typing import Dict, List
import logging
from uuid import uuid4
from sqlalchemy import create_engine, Column, String, Boolean, Text, DateTime, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import psycopg2
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from sqlalchemy import text


load_dotenv()

logging.basicConfig(level=logging.ERROR)

DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_NAME = os.getenv("DATABASE_NAME")

DATABASE_URL =  f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

logging.info(DATABASE_URL)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



def ensure_database_exists():
    try:
        test_engine = create_engine(DATABASE_URL)
        test_engine.connect()
        logging.info(f"Database {DATABASE_NAME} exists")
    except OperationalError as e:
        if 'database "posts" does not exist' in str(e):
            logging.info(f"Database {DATABASE_NAME} not found, attempting to create it")
            
            # Connect to default postgres database to create our target db
            admin_url = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/postgres"
            admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
            
            try:
                with admin_engine.connect() as conn:
                    conn.execute(text(f"CREATE DATABASE {DATABASE_NAME}"))
                logging.info(f"Successfully created database {DATABASE_NAME}")
            except Exception as create_error:
                logging.error(f"Failed to create database: {create_error}")
                raise
        else:
            raise

class PostDB(Base):
    __tablename__ = "posts"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    creator_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_private = Column(Boolean, default=False)
    tags = Column(ARRAY(String))

# Initialize the database
def init_db():
    ensure_database_exists()
    Base.metadata.create_all(bind=engine)
    logging.info("Database tables created")


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
        self.db = SessionLocal()

    def CreatePost(self, request, context):
        try:
            post_id = str(uuid4())
            new_post = PostDB(
                id=post_id,
                title=request.title,
                description=request.description,
                creator_id=request.creator_id,
                is_private=request.is_private if request.is_private else False,
                tags=list(request.tags)
            )
            
            self.db.add(new_post)
            self.db.commit()
            self.db.refresh(new_post)

            return service_pb2.PostResponse(post=self._post_to_proto(new_post))
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error creating post: {str(e)}")
            return service_pb2.PostResponse()

    def GetPost(self, request, context):
        try:
            post = self.db.query(PostDB).filter(PostDB.id == request.id).first()
            if not post:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Post not found")
                return service_pb2.PostResponse()
            
            return service_pb2.PostResponse(post=self._post_to_proto(post))
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error retrieving post: {str(e)}")
            return service_pb2.PostResponse()

    def UpdatePost(self, request, context):
        try:
            post = self.db.query(PostDB).filter(PostDB.id == request.id).first()
            if not post:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Post not found")
                return service_pb2.PostResponse()

            if request.title:
                post.title = request.title
            if request.description:
                post.description = request.description
            if request.is_private is not None:
                post.is_private = request.is_private
            if request.tags:
                post.tags = list(request.tags)
            
            post.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(post)
            return service_pb2.PostResponse(post=self._post_to_proto(post))
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error updating post: {str(e)}")
            return service_pb2.PostResponse()

    def DeletePost(self, request, context):
        db = SessionLocal()
        try:
            post = db.query(PostDB).filter(PostDB.id == request.id).first()
            if not post:
                db.close()
                return service_pb2.DeletePostResponse(success=False)

            if post.creator_id != request.deleter_id:
                db.close()
                return service_pb2.DeletePostResponse(success=False)

            db.delete(post)
            db.commit()
            return service_pb2.DeletePostResponse(success=True)

        except Exception as e:
            db.rollback()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error deleting post: {str(e)}")
            return service_pb2.DeletePostResponse(success=False)
        finally:
            db.close()

    def ListPosts(self, request, context):
        try:
            page = max(1, request.page)
            per_page = max(1, min(request.per_page, 100))  
            offset = (page - 1) * per_page

            query = self.db.query(PostDB)
            if request.user_id:
                query = query.filter((PostDB.is_private == False) | (PostDB.creator_id == request.user_id))

            total = query.count()
            posts = query.order_by(PostDB.created_at.desc()).offset(offset).limit(per_page).all()

            return service_pb2.ListPostsResponse(
                posts=[self._post_to_proto(post) for post in posts],
                total=total,
                page=page,
                per_page=per_page
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error listing posts: {str(e)}")
            return service_pb2.ListPostsResponse()

    def _post_to_proto(self, post) -> service_pb2.Post:
        return service_pb2.Post(
            id=post.id,
            title=post.title,
            description=post.description,
            creator_id=post.creator_id,
            created_at=self._datetime_to_timestamp(post.created_at),
            updated_at=self._datetime_to_timestamp(post.updated_at),
            is_private=post.is_private,
            tags=post.tags
        )

    def _datetime_to_timestamp(self, dt: datetime) -> Timestamp:
        timestamp = Timestamp()
        timestamp.FromDatetime(dt)
        return timestamp


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_PostServiceServicer_to_server(PostServiceImpl(), server)
    server.add_insecure_port('0.0.0.0:8091')
    server.start()
    logging.info("Posts gRPC server started on port 8091")
    
    try:
        server.wait_for_termination()
    finally:
        SessionLocal().close()  # Close DB session on shutdown


if __name__ == '__main__':
    init_db()
    serve()