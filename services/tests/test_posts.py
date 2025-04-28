import json
import logging
import os
import socket
import time
import urllib
import uuid

import jwt
import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

LOGGER = logging.getLogger(__name__)

def wait_for_socket(host, port):
    retries = 10
    exception = None
    while retries > 0:
        try:
            socket.socket().connect((host, port))
            return
        except ConnectionRefusedError as e:
            exception = e
            print(f'Got ConnectionError for url {host}:{port}: {e} , retrying')
            retries -= 1
            time.sleep(2)
    raise exception

def make_requests(method, addr, handle, params=None, data=None, cookies=None):
    if data is not None:
        data = json.dumps(data)
    req = requests.Request(method, addr + handle, params=params, data=data, cookies=cookies)
    s = requests.Session()
    resp = s.send(req.prepare())
    return resp

def make_user(auth_addr):
    username = str(uuid.uuid4())
    password = str(uuid.uuid4())
    email = f"{username}@example.com"
    r = make_requests('POST', auth_addr, '/signup', 
                     data={'username': username, 'password': password, 'email': email})
    assert r.status_code == 200
    cookies = r.cookies.get_dict()
    return ((username, password), cookies)

def login_user(auth_addr, user):
    ((username, password), _) = user
    r = make_requests('POST', auth_addr, '/login', 
                     data={'username': username, 'password': password})
    assert r.status_code == 200
    return r.cookies.get_dict()


@pytest.fixture
def auth_addr():
    addr = os.environ.get('PROXY_AUTH_URL', 'http://gateway_api:5000/users')
    host = urllib.parse.urlparse(addr).hostname
    port = urllib.parse.urlparse(addr).port
    wait_for_socket(host, port)
    yield addr


@pytest.fixture
def posts_addr():
    addr = os.environ.get('PROXY_POSTS_URL', 'http://gateway_api:5000/posts')
    host = urllib.parse.urlparse(addr).hostname
    port = urllib.parse.urlparse(addr).port
    wait_for_socket(host, port)
    yield addr


@pytest.fixture
def jwt_private():
    key = os.environ.get('PRIVATE_KEY', 'secret')
    yield key


@pytest.fixture
def jwt_public():
    key = os.environ.get('PUBLIC_KEY', 'secret')
    yield key

class TestPosts:
    @staticmethod
    def test_create_post(posts_addr, auth_addr):
        # Setup
        user = make_user(auth_addr)
        cookies = login_user(auth_addr, user)

        post_data = {
            'title': 'Test Post',
            'description': 'This is a test post',
            'is_private': False,
            'tags': ['test', 'example']
        }
        r = make_requests('POST', posts_addr, '/posts', data=post_data, cookies=cookies)
        
        # Assertions
        assert r.status_code == 201
        response_data = r.json()
        assert 'id' in response_data
        assert response_data['title'] == post_data['title']
        return response_data['id']

    @staticmethod
    def test_get_post(posts_addr, auth_addr):
        # Create test post
        post_id = TestPosts.test_create_post(posts_addr, auth_addr)
        user = make_user(auth_addr)
        cookies = login_user(auth_addr, user)
        
        # Test public post access
        r = make_requests('GET', posts_addr, f'/posts/{post_id}', cookies=cookies)
        assert r.status_code == 200
        assert r.json()['id'] == post_id
        
        # Test private post access
        private_post_data = {
            'title': 'Private Post',
            'description': 'This is a test post',
            'is_private': True,
            'tags': ['test', 'example']
        }
        r_private = make_requests('POST', posts_addr, '/posts', 
                                data=private_post_data, cookies=cookies)
        private_post_id = r_private.json()['id']
        
        # Should fail for other users
        other_user = make_user(auth_addr)
        other_cookies = login_user(auth_addr, other_user)
        r_fail = make_requests('GET', posts_addr, f'/posts/{private_post_id}', 
                             cookies=other_cookies)
        assert r_fail.status_code == 403

    @staticmethod
    def test_list_posts(posts_addr, auth_addr):
        user = make_user(auth_addr)
        cookies = login_user(auth_addr, user)
        
        # Create multiple posts
        for i in range(5):
            make_requests('POST', posts_addr, '/posts', 
                         data={'title': f'Post {i}'}, cookies=cookies)
        
        # Test pagination
        r = make_requests('GET', posts_addr, '/posts/list', 
                         params={'page': 1, 'per_page': 3}, cookies=cookies)
        assert r.status_code == 200
        data = r.json()
        assert len(data['posts']) == 3
        assert data['page'] == 1
        assert data['per_page'] == 3
        assert data['total'] >= 5

    @staticmethod
    def test_update_post(posts_addr, auth_addr):
        user = make_user(auth_addr)
        cookies = login_user(auth_addr, user)
        
        # Create test post
        post_data = {
            'title': 'Test Post',
            'description': 'This is a test post',
            'is_private': False,
            'tags': ['test', 'example']
        }
        r = make_requests('POST', posts_addr, '/posts', data=post_data, cookies=cookies)
        
        # Assertions
        assert r.status_code == 201
        response_data = r.json()
        assert 'id' in response_data
        assert response_data['title'] == post_data['title']
        
        # Update post
        update_data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'updater_id': user[0][0],
            'is_private': True,
        }
        post_id = response_data['id']
        r = make_requests('PUT', posts_addr, f'/posts/{post_id}', 
                         data=update_data, cookies=cookies)
        assert r.status_code == 200
        
        # Verify update
        r_get = make_requests('GET', posts_addr, f'/posts/{post_id}', cookies=cookies)
        assert r_get.json()['title'] == update_data['title']

    @staticmethod
    def test_delete_post(posts_addr, auth_addr):
        user = make_user(auth_addr)
        cookies = login_user(auth_addr, user)
        
        post_data = {
            'title': 'Test Post',
            'description': 'This is a test post',
            'is_private': False,
            'tags': ['test', 'example']
        }
        r = make_requests('POST', posts_addr, '/posts', data=post_data, cookies=cookies)
        
        assert r.status_code == 201
        response_data = r.json()
        assert 'id' in response_data
        assert response_data['title'] == post_data['title']

        post_id = response_data['id']
        
        r = make_requests('DELETE', posts_addr, f'/posts/{post_id}', 
                         data={'deleter_id': user[0][0]}, cookies=cookies)
        assert r.status_code == 200
        
class TestPostsAuthorization:
    @staticmethod
    def test_unauthorized_access(posts_addr):
        r_create = make_requests('POST', posts_addr, '/posts', 
                                data={'title': 'Unauthorized'})
        assert r_create.status_code == 401
        
        r_list = make_requests('GET', posts_addr, '/posts')
        assert r_list.status_code == 401

    @staticmethod
    def test_cannot_update_others_posts(posts_addr, auth_addr):
        # User 1 creates post
        user1 = make_user(auth_addr)
        cookies1 = login_user(auth_addr, user1)
        post_id = TestPosts.test_create_post(posts_addr, auth_addr)
        
        # User 2 tries to update
        user2 = make_user(auth_addr)
        cookies2 = login_user(auth_addr, user2)
        r = make_requests('PUT', posts_addr, f'/posts/{post_id}', 
                         data={'title': 'Hacked'}, cookies=cookies2)
        assert r.status_code == 403

class TestPostsLikes:
    @staticmethod
    def test_like_post(posts_addr, auth_addr):
        user = make_user(auth_addr)
        cookies = login_user(auth_addr, user)
        
        post_id = TestPosts.test_create_post(posts_addr, auth_addr)

        logging.fatal(f"{post_id}")

        r_like = make_requests('POST', posts_addr, f'/posts/{str(post_id)}/like', 
                             cookies=cookies)
        assert r_like.status_code == 200
        assert r_like.json() == {"success": "Liked"}
    
    @staticmethod
    def test_unauthorized_like(posts_addr):
        r_like = make_requests('POST', posts_addr, '/posts/123/like')
        assert r_like.status_code == 401
    
    @staticmethod
    def test_like_nonexistent_post(posts_addr, auth_addr):
        user = make_user(auth_addr)
        cookies = login_user(auth_addr, user)
        
        r_like = make_requests('POST', posts_addr, '/posts/999999/like', 
                             cookies=cookies)
        assert r_like.status_code in [404, 500]

class TestPostsComments:
    @staticmethod
    def test_comment_post(posts_addr, auth_addr):
        user = make_user(auth_addr)
        cookies = login_user(auth_addr, user)
        
        post_id = TestPosts.test_create_post(posts_addr, auth_addr)
        
        r_comment = make_requests('POST', posts_addr, f'/posts/{post_id}/comment',
                                data={'text': 'Test comment'}, cookies=cookies)
        assert r_comment.status_code == 200
        assert r_comment.json() == {"success": "Comment"}
    
    @staticmethod
    def test_unauthorized_comment(posts_addr):
        r_comment = make_requests('POST', posts_addr, '/posts/123/comment',
                                data={'text': 'Test comment'})
        assert r_comment.status_code == 401
    
    @staticmethod
    def test_comment_nonexistent_post(posts_addr, auth_addr):
        user = make_user(auth_addr)
        cookies = login_user(auth_addr, user)
        
        r_comment = make_requests('POST', posts_addr, '/posts/999999/comment',
                                data={'text': 'Test comment'}, cookies=cookies)
        assert r_comment.status_code in [404, 500]
