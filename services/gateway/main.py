from flask import Flask, request, jsonify
import requests
import logging
import os
from dotenv import load_dotenv
from posts_client import PostServiceClient
import jwt
import time

load_dotenv()

app = Flask(__name__)

USERS_API_URL = os.environ.get('USERS_API_URL', 'http://auth:8090')
POSTS_API_URL = os.environ.get('POSTS_API_URL',  'posts:8091')
STATS_API_URL = os.environ.get('STATS_API_URL',   'http://stats:8092')

private_key = os.getenv("PRIVATE_KEY")
public_key = os.getenv("PUBLIC_KEY")

pc = PostServiceClient(POSTS_API_URL)

logging.basicConfig(level=logging.INFO)

@app.route("/users/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_users(path):
    """ Proxy requests to the Users Service at `/users/` """
    url = f"{USERS_API_URL}/{path}"

    logging.info(f"Forwarding {request.method} request to {url}")

    try:
        data = request.get_json(silent=True, force=True)

        resp = requests.request(
            method=request.method,
            url=url,
            json=data,
            cookies=request.cookies,
        )

        return (resp.content, resp.status_code, resp.headers.items())

    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
        return jsonify({"error": "Failed to connect to User Service API"}), 500
    


###############################################################################################################

def check_auth(user_id, request):
    try:
        req = requests.Request("GET", f"{USERS_API_URL}/sessions", data=request.get_json(silent=True, force=True), cookies=request.cookies)
        s = requests.Session()
        response = s.send(req.prepare())

        if response.status_code == 200:
            sessions = response.json()
            if sessions and len(sessions) > 0:
                logging.debug(f"Valid session found for user {user_id}")
                return True
            
        logging.warning(f"No active sessions found for user {user_id}")
        return False

    except requests.exceptions.RequestException as e:
        logging.error(f"Auth service unreachable: {str(e)}")
        return False
    except ValueError as e:
        logging.error(f"Invalid response from auth service: {str(e)}")
        return False

def get_username_from_token(request):
    token = request.cookies.get('jwt')
    if not token:
        logging.warning("No JWT token found in cookies")
        return None

    try:
        decoded = jwt.decode(token, public_key, algorithms=['RS256'])
        return decoded.get('username')
    except jwt.ExpiredSignatureError:
        logging.warning("Expired JWT token")
        return None
    except jwt.InvalidTokenError:
        logging.warning("Invalid JWT token")
        return None
    except Exception as e:
        logging.error(f"Unexpected token decoding error: {str(e)}")
        return None

@app.route("/posts/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_posts(path):
    try:
        username = get_username_from_token(request)
        if not check_auth(username, request):
            return jsonify({"error": "Unauthorized"}), 401

        if request.method == "GET":
            if path.split("posts/")[1] != "list":
                post = pc.get_post(post_id=path.split("posts/")[1], user_id=username)
                logging.info(f"Get Post: {post}")
                # Check if post is private and user is not the creator
                if post['is_private'] and post['creator_id'] != request['user_id']:
                    return jsonify({"error": "You are not allows to view this post"}), 403
                return jsonify(post)
            else:
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 10, type=int)
                posts = pc.list_posts(page=page, per_page=per_page, user_id=username)
                return jsonify([{
                    "id": p.id,
                    "title": p.title,
                    "creator_id": p.creator_id
                } for p in posts])

        elif request.method == "POST":
            data = request.get_json()
            new_post = pc.create_post({
                "title":data['title'],
                "description":data.get('description', ''),
                "creator_id": username,
                "is_private": data.get('is_private', False),
                "tags":data.get('tags', [])
                }
            )
            logging.info(f"{new_post}")
            return jsonify(new_post), 201

        elif request.method == "PUT":
            data = request.get_json()
            updated_post = pc.update_post(
                post_id=int(path),data={
                "title":data.get('title'),
                "description": data.get('description'),
                "updater_id":username,
                "is_private":data.get('is_private'),
                "tags":data.get('tags', [])
                }
            )
            return jsonify({"status": "success", "post_id": updated_post.id})

        elif request.method == "DELETE":
            deleter_id = request.args.get('deleter_id', '')
            success = pc.delete_post(post_id=int(path), deleter_id=deleter_id)
            return jsonify({"status": "success" if success else "failed"}), 200 if success else 403

    except Exception as e:
        logging.error(f"Posts service error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/stats/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_stats(path):
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
