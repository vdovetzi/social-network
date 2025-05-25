import pytest
import json
import uuid
from test_users import make_requests, make_user, wait_for_socket
from test_posts import login_user, TestPosts, TestPostsComments, TestPostsLikes
import os
import urllib
import time
import socket

@pytest.fixture
def auth_addr():
    addr = os.environ.get('PROXY_AUTH_URL', 'http://gateway_api:5000/users')
    host = urllib.parse.urlparse(addr).hostname
    port = urllib.parse.urlparse(addr).port
    wait_for_socket(host, port)
    yield addr

@pytest.fixture
def stats_addr():
    addr = os.environ.get('PROXY_STATS_URL', 'http://gateway_api:5000/stats')
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

class TestStatistics:
    def test_get_statistics_unauthorized(self, stats_addr):
        r = make_requests('GET', stats_addr, f"/overview?post_id=123")
        assert r.status_code == 401

    def test_get_statistics_authorized(self, posts_addr, stats_addr, auth_addr):
        user = make_user(auth_addr)
        cookies = login_user(auth_addr, user)

        post_id = TestPosts.test_create_post(posts_addr, auth_addr)

        r = make_requests('GET', stats_addr, f"/overview?post_id={post_id}", cookies=cookies)
        assert r.status_code == 200
        data = r.json()
        assert 'likes_count' in data
        assert 'comments_count' in data
        assert 'views_count' in data

    def test_get_post_stats(self, posts_addr, stats_addr, auth_addr):
        user = make_user(auth_addr)
        cookies = login_user(auth_addr, user)
        post_id = TestPosts.test_create_post(posts_addr, auth_addr)

        r = make_requests("GET", stats_addr, f"/post/{post_id}", cookies=cookies)
        assert r.status_code == 200
        data = r.json()
        assert data["post_id"] == post_id
        assert "views" in data and "likes" in data and "comments" in data

    def test_get_views_dynamic(self, posts_addr, stats_addr, auth_addr):
        user = make_user(auth_addr)
        cookies = login_user(auth_addr, user)
        post_id = TestPosts.test_create_post(posts_addr, auth_addr)

        r = make_requests("GET", stats_addr, f"/views/{post_id}", cookies=cookies)
        assert r.status_code == 200
        assert isinstance(r.json()["views"], list)

    def test_get_top_posts(self, stats_addr, auth_addr):
        user = make_user(auth_addr)
        cookies = login_user(auth_addr, user)

        r = make_requests("GET", stats_addr, "/top/posts", cookies=cookies)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data["posts"], list)

    def test_get_top_users(self, stats_addr, auth_addr):
        user = make_user(auth_addr)
        cookies = login_user(auth_addr, user)

        r = make_requests("GET", stats_addr, "/top/users", cookies=cookies)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data["users"], list)

    def test_statistics_counts_increment(self, posts_addr, stats_addr, auth_addr):
        user = make_user(auth_addr)
        cookies = login_user(auth_addr, user)

        post_id = TestPosts.test_create_post(posts_addr, auth_addr)

        r1 = make_requests("GET", stats_addr, f"/overview?post_id={post_id}", cookies=cookies)
        stats_before = r1.json()

        r_comment = make_requests('POST', posts_addr, f'/posts/{post_id}/comment', data={'text': 'Test comment'}, cookies=cookies)
        assert r_comment.status_code == 200
        assert r_comment.json() == {"success": "Comment"}

        r_like = make_requests('POST', posts_addr, f'/posts/{str(post_id)}/like', 
                             cookies=cookies)
        assert r_like.status_code == 200
        assert r_like.json() == {"success": "Liked"}

        r = make_requests('GET', posts_addr, f'/posts/{post_id}', cookies=cookies)
        assert r.status_code == 200
        assert r.json()['id'] == post_id

        time.sleep(2)

        r2 = make_requests("GET", stats_addr, f"/overview?post_id={post_id}", cookies=cookies)
        stats_after = r2.json()

        assert stats_after["likes_count"] > stats_before["likes_count"]
        assert stats_after["views_count"] > stats_before["views_count"]
        assert stats_after["comments_count"] > stats_before["comments_count"]