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


@pytest.fixture
def auth_addr():
    addr = os.environ.get('PROXY_SERVER_URL', 'http://gateway_api:5000/users')
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


def make_requests(method, addr, handle, params=None, data=None, cookies=None):
    if data is not None:
        data = json.dumps(data)
    req = requests.Request(
        method,
        addr +
        handle,
        params=params,
        data=data,
        cookies=cookies)
    prepared = req.prepare()
    LOGGER.info(f'>>> {prepared.method} {prepared.url}')
    if len(req.data) > 0:
        LOGGER.info(f'>>> {req.data}')
    if req.cookies is not None:
        LOGGER.info(f'>>> {req.cookies}')
    s = requests.Session()
    resp = s.send(prepared)
    LOGGER.info(f'<<< {resp.status_code}')
    if len(resp.content) > 0:
        LOGGER.info(f'<<< {resp.content}')
    if len(resp.cookies) > 0:
        LOGGER.info(f'<<< {resp.cookies}')
    return resp


def make_user(auth_addr):
    username = str(uuid.uuid4())
    password = str(uuid.uuid4())
    email =  str(uuid.uuid4())+"@gmail.com"
    r = make_requests(
        'POST',
        auth_addr,
        '/signup',
        data={
            'username': username,
            'password': password,
            'email': email})
    assert r.status_code == 200
    cookies = r.cookies.get_dict()
    return ((username, password), cookies)


@pytest.fixture
def user(auth_addr):
    yield make_user(auth_addr)


@pytest.fixture
def another_user(auth_addr):
    yield make_user(auth_addr)


def generate_jwt(private, username):
    return jwt.encode({'username': username}, private, 'RS256')


def parse_jwt(token, public):
    return jwt.decode(token, public, ['RS256'])


def generate_hs256_jwt(secret, username):
    return jwt.encode({'username': username}, secret, 'HS256')

class TestDropTables:
    @staticmethod
    def test_drop_tables(auth_addr, user):
        ((_, _), cookies) = user
        r = make_requests(
            'DELETE',
            auth_addr,
            '/drop_tables',
            data={"tables": ["users", "user_roles", "sessions", "user_profiles"]},
            cookies=cookies)
        assert r.status_code == 200

class TestRSA:
    @staticmethod
    def test_private(jwt_private):
        generate_jwt(jwt_private, 'test')

    @staticmethod
    def test_public(jwt_private, jwt_public):
        token = generate_jwt(jwt_private, 'test')
        decoded = parse_jwt(token, jwt_public)
        assert decoded['username'] == 'test'


class TestAuth:
    @staticmethod
    def check_jwt(cookies, public, username):
        token = cookies['jwt']
        decoded = parse_jwt(token, public)
        assert decoded['username'] == username

    @staticmethod
    def test_signup(jwt_public, user):
        ((username, _), cookies) = user
        TestAuth.check_jwt(cookies, jwt_public, username)

    @staticmethod
    def test_signup_with_existing_user(auth_addr, user):
        ((username, _), _) = user
        password = str(uuid.uuid4())
        email = str(uuid.uuid4())+"@example.com"
        r = make_requests(
            'POST',
            auth_addr,
            '/signup',
            data={
                'username': username,
                'password': password,
                'email': email})
        assert r.status_code == 403
        assert len(r.cookies) == 0

    @staticmethod
    def test_login(auth_addr, jwt_public, user):
        ((username, password), _) = user
        r = make_requests(
            'POST',
            auth_addr,
            '/login',
            data={
                'username': username,
                'password': password})
        assert r.status_code == 200
        TestAuth.check_jwt(r.cookies, jwt_public, username)

    @staticmethod
    def test_login_with_wrong_password(auth_addr, user):
        ((username, _), _) = user
        password = str(uuid.uuid4())
        r = make_requests(
            'POST',
            auth_addr,
            '/login',
            data={
                'username': username,
                'password': password})
        assert r.status_code == 403
        assert len(r.cookies) == 0

    @staticmethod
    def test_login_with_non_existing_user(auth_addr):
        username = str(uuid.uuid4())
        password = str(uuid.uuid4())
        r = make_requests(
            'POST',
            auth_addr,
            '/login',
            data={
                'username': username,
                'password': password})
        assert r.status_code == 403
    
    @staticmethod
    def test_signup_duplicate_email(auth_addr):
        username = str(uuid.uuid4())
        password = str(uuid.uuid4())
        email = str(uuid.uuid4()) + "@example.com"
        user_data = {
            "username": username,
            "password": password,
            "email": email
        }
        r = requests.post(f"{auth_addr}/signup", json=user_data)
        assert r.status_code == 200
        
        username = str(uuid.uuid4())
        password = str(uuid.uuid4())
        user_data = {
            "username": username,
            "password": password,
            "email": email
        }
        r = requests.post(f"{auth_addr}/signup", json=user_data)
        
        assert r.status_code == 403

    @staticmethod
    def test_signup_invalid_email(auth_addr):
        user_data = {
            "username": "invalidemailuser",
            "password": "Pass123!",
            "email": "notanemail"
        }
        r = requests.post(f"{auth_addr}/signup", json=user_data)
        assert r.status_code == 400

class TestProfile:
    @staticmethod
    def test_get_profile(auth_addr, user):
        ((_, _), cookies) = user
        r = requests.get(f"{auth_addr}/profile", cookies=cookies)
        assert r.status_code == 200
        profile_data = r.json()
        assert "birthdate" in profile_data
        assert "email" in profile_data
        assert "created_at" in profile_data
        assert "first_name" in profile_data
        assert "username" in profile_data
        assert "phone_number" in profile_data
        assert "last_name" in profile_data
        assert "bio" in profile_data

    @staticmethod
    def test_get_profile_unauthorized(auth_addr):
        r = requests.get(f"{auth_addr}/profile")
        assert r.status_code == 401

    @staticmethod
    def test_update_profile(auth_addr, user):
        ((_, _), cookies) = user
        new_data = {"first_name": "John"}
        
        r = requests.put(f"{auth_addr}/profile", json=new_data, cookies=cookies)
        assert r.status_code == 200

        r = requests.get(f"{auth_addr}/profile", cookies=cookies)
        assert r.status_code == 200
        profile_data = r.json()
        assert profile_data.get("first_name") == "John"

    @staticmethod
    def test_update_profile_unauthorized(auth_addr):
        r = requests.put(f"{auth_addr}/profile", json={"first_name": "John"})
        assert r.status_code == 401
    
    @staticmethod
    def test_cannot_update_username(auth_addr, user):
        ((_, _), cookies) = user
        r = requests.put(f"{auth_addr}/profile", json={"username": "new_username"}, cookies=cookies)
        assert r.status_code == 400

        r = requests.get(f"{auth_addr}/profile", cookies=cookies)
        assert r.status_code == 200
        profile_data = r.json()
        assert profile_data.get("username") != "new_username"

    @staticmethod
    def test_cannot_update_password(auth_addr, user):
        ((_, _), cookies) = user
        r = requests.put(f"{auth_addr}/profile", json={"password": "new_password"}, cookies=cookies)
        assert r.status_code == 400
        
    @staticmethod
    def test_cannot_update_nonexistent_field(auth_addr, user):
        ((_, _), cookies) = user
        r = requests.put(f"{auth_addr}/profile", json={"kitty": "yes"}, cookies=cookies)
        assert r.status_code == 400
        
import json
import uuid
import requests
import pytest

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
    email = str(uuid.uuid4()) + "@gmail.com"
    r = make_requests('POST', auth_addr, '/signup', data={'username': username, 'password': password, 'email': email})
    assert r.status_code == 200
    cookies = r.cookies.get_dict()
    return ((username, password), cookies)

class TestRoles:
    @staticmethod
    def test_assign_role(auth_addr, jwt_public, user):
        TestAuth.test_login(auth_addr, jwt_public, user)
        ((_, _), cookies) = user
        r = make_requests('POST', auth_addr, '/roles', data={'role_name': 'admin'}, cookies=cookies)
        assert r.status_code == 200
        
    @staticmethod
    def test_assign_role_again(auth_addr, jwt_public):
        user = make_user(auth_addr)
        TestAuth.test_login(auth_addr, jwt_public, user)
        ((_, _), cookies) = user
        r = make_requests('POST', auth_addr, '/roles', data={'role_name': 'admin'}, cookies=cookies)
        assert r.status_code == 200
        r = make_requests('POST', auth_addr, '/roles', data={'role_name': 'manager'}, cookies=cookies)
        assert r.status_code == 200

    @staticmethod
    def test_get_roles(auth_addr, jwt_public):
        user = make_user(auth_addr)
        TestAuth.test_login(auth_addr, jwt_public, user)
        ((_, _), cookies) = user
        r = make_requests('POST', auth_addr, '/roles', data={'role_name': 'admin'}, cookies=cookies)
        assert r.status_code == 200
        r = make_requests('POST', auth_addr, '/roles', data={'role_name': 'manager'}, cookies=cookies)
        assert r.status_code == 200
        r = make_requests('GET', auth_addr, '/roles', cookies=cookies)
        assert r.status_code == 200
        assert len(r.json()) == 2
        roles = [r.json()[0]["role_name"], r.json()[1]["role_name"]]
        assert 'admin' in roles
        assert 'manager' in roles
    
    @staticmethod
    def test_cannot_assign_the_same_role_twice(auth_addr, jwt_public):
        user = make_user(auth_addr)
        TestAuth.test_login(auth_addr, jwt_public, user)
        ((_, _), cookies) = user 
        r = make_requests('POST', auth_addr, '/roles', data={'role_name': 'admin'}, cookies=cookies)
        assert r.status_code == 200
        r = make_requests('POST', auth_addr, '/roles', data={'role_name': 'admin'}, cookies=cookies)
        assert r.status_code == 409
    
    @staticmethod
    def test_delete_role(auth_addr, jwt_public):
        user = make_user(auth_addr)
        TestAuth.test_login(auth_addr, jwt_public, user)
        ((_, _), cookies) = user
        r = make_requests('POST', auth_addr, '/roles', data={'role_name': 'admin'}, cookies=cookies)
        assert r.status_code == 200
        r = make_requests('GET', auth_addr, '/roles', cookies=cookies)
        assert r.status_code == 200
        assert len(r.json()) == 1
        assert "admin" == r.json()[0]["role_name"]
        r = make_requests('DELETE', auth_addr, f'/roles', data={"role_name": "admin"}, cookies=cookies)
        assert r.status_code == 200
        r = make_requests('GET', auth_addr, '/roles', cookies=cookies)
        assert r.status_code == 200
        assert len(r.json()) == 0

class TestSessions:
    @staticmethod
    def test_list_sessions(auth_addr, user):
        ((_, _), cookies) = user
        r = make_requests('GET', auth_addr, '/sessions', cookies=cookies)
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        return r.json()

    @staticmethod
    def test_logout(auth_addr, user):
        sessions = TestSessions.test_list_sessions(auth_addr, user)
        ((_, _), cookies) = user
        for session in sessions:
            r = make_requests('POST', auth_addr, '/logout', data={"session_id": session["session_id"]}, cookies=cookies)
            assert r.status_code == 200