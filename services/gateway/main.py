from flask import Flask, request, jsonify
import requests
import logging
import os
from dotenv import load_dotenv
from posts_client import PostServiceClient
from stats_client import StatisticsClient, statistics_pb2
import jwt
from kafka_producer import send_like_event, send_view_event, send_comment_event
import grpc
import uuid

load_dotenv()

app = Flask(__name__)

USERS_API_URL = os.environ.get('USERS_API_URL', 'http://auth:8090')
POSTS_API_URL = os.environ.get('POSTS_API_URL',  'posts:8091')
STATS_API_URL = os.environ.get('STATS_API_URL',   'statistics:8092')

private_key = os.getenv("PRIVATE_KEY")
public_key = os.getenv("PUBLIC_KEY")

pc = PostServiceClient(POSTS_API_URL)
sc = StatisticsClient(STATS_API_URL)

logging.basicConfig(level=logging.ERROR)

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

def check_post_exists(user_id, post_id):
    try:
        post = pc.get_post(post_id=post_id, user_id=user_id)
        if post.is_private and post.creator_id != user_id:
                return False
        return True
    except:
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

def post_to_dict(post):
    return {
        'id': post.id,
        'title': post.title,
        'description': post.description,
        'creator_id': post.creator_id,
        'created_at': post.created_at.ToDatetime(),
        'updated_at': post.updated_at.ToDatetime(),
        'is_private': post.is_private,
        'tags': list(post.tags)
    }

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

                if post.is_private and post.creator_id != username:
                    return jsonify({"error": "You are not allows to view this post"}), 403
                
                send_view_event(username, str(post.id))
                
                return jsonify(post_to_dict(post))
            else:
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 10, type=int)
                posts = pc.list_posts(page=page, per_page=per_page, user_id=username)
                logging.info(f"{posts}")

                for post in posts['posts']:
                    send_view_event(username, str(post['id']))

                return jsonify({"posts": [{
                    "id": p['id'],
                    "title": p['title'],
                    "creator_id": p['creator_id']
                } for p in posts['posts']],
                    "total": posts['total'],
                    "page": posts['page'],
                    "per_page": posts['per_page']
                })

        elif request.method == "POST":
            if path.split('/')[-1] == "like":
                try:
                    post_id = path.split('/')[-2]
                    if not check_post_exists(username, post_id):
                        return jsonify({"error": "Post does not exist"}), 500
                    send_like_event(username, str(post_id))
                    return jsonify({"success": "Liked"}), 200
                except Exception as e:
                    logging.error(f"Like request failed: {e}")
                    return jsonify({"error": "Like failed"}), 500
            elif path.split('/')[-1] == "comment":
                data = request.get_json()
                comment_text = data.get('text')
                post_id = path.split('/')[-2]
                try:
                    if not check_post_exists(username, post_id):
                        return jsonify({"error": "Post does not exist"}), 500
                    send_comment_event(username, str(post_id), str(uuid.uuid4()))
                    return jsonify({"success": "Comment"}), 200
                except Exception as e:
                    logging.error(f"Comment request failed: {e}")
                    return jsonify({"error": "Comment failed"}), 500
            else:
                data = request.get_json()
                new_post = pc.create_post({
                    "title":data['title'],
                    "description":data.get('description', ''),
                    "creator_id": username,
                    "is_private": data.get('is_private', False),
                    "tags":data.get('tags', [])
                    }
                )
                logging.info(f"Created Post ID: {new_post['id']}")
                return jsonify(new_post), 201

        elif request.method == "PUT":
            data = request.get_json()

            post = pc.get_post(post_id=path.split("posts/")[1], user_id=username)

            if post.creator_id != username:
                return jsonify({"error": "You are not allowed to update this post"}), 403

            updated_post = pc.update_post(
                post_id=path.split("posts/")[1],data={
                "title":data.get('title'),
                "description": data.get('description'),
                "updater_id":username,
                "is_private":data.get('is_private'),
                "tags":data.get('tags', [])
                }
            )
            return jsonify(post_to_dict(updated_post))
        elif request.method == "DELETE":
            deleter_id = request.args.get('deleter_id', '')
            post_id =  path.split("posts/")[1]
            logging.info(f"Deleting Post with ID: {post_id}")
            success = pc.delete_post(post_id=post_id, deleter_id=deleter_id)
            return jsonify({"status": "success" if success else "failed"}), 200 if success else 403
    except Exception as e:
        import traceback
        traceback.print_exc()
        logging.error(f"Posts service error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/stats/<path:path>", methods=["GET"])
def proxy_stats(path):
    try:
        username = get_username_from_token(request)
        logging.warning(f"HERE WITH {username} and {request}")
        if not check_auth(username, request):
            return jsonify({"error": "Unauthorized"}), 401
        

        segments = path.strip("/").split("/")

        logging.error(f"{segments}")
        
        if len(segments) == 2 and segments[0] in ["post", "views", "likes", "comments"]:
            post_id = segments[1]
            if segments[0] == "post":
                stats = sc.get_post_stats(post_id)
                return jsonify({
                    "post_id": post_id,
                    "views": stats.views,
                    "likes": stats.likes,
                    "comments": stats.comments
                })
            elif segments[0] == "views":
                res = sc.get_views_dynamic(post_id)
                return jsonify({
                    "post_id": post_id,
                    "views": [{"date": d.date, "count": d.count} for d in res.data]
                })
            elif segments[0] == "likes":
                res = sc.get_likes_dynamic(post_id)
                return jsonify({
                    "post_id": post_id,
                    "likes": [{"date": d.date, "count": d.count} for d in res.data]
                })
            elif segments[0] == "comments":
                res = sc.get_comments_dynamic(post_id)
                return jsonify({
                    "post_id": post_id,
                    "comments": [{"date": d.date, "count": d.count} for d in res.data]
                })

        elif path == "top/posts":
            metric = request.args.get("metric", "VIEWS").upper()
            enum_val = statistics_pb2.Metric.Value(metric)
            res = sc.get_top_posts(enum_val)
            return jsonify({
                "posts": [{"post_id": p.post_id, "count": p.count} for p in res.posts]
            })

        elif path == "top/users":
            metric = request.args.get("metric", "LIKES").upper()
            enum_val = statistics_pb2.Metric.Value(metric)
            res = sc.get_top_users(enum_val)
            return jsonify({
                "users": [{"user_id": u.user_id, "count": u.count} for u in res.users]
            })

        elif path == "overview":
            post_id = request.args.get("post_id")
            if not post_id:
                return jsonify({"error": "post_id is required"}), 400
            return jsonify({
                "views_count": len(sc.get_views_dynamic(post_id).data),
                "likes_count": len(sc.get_likes_dynamic(post_id).data),
                "comments_count": len(sc.get_comments_dynamic(post_id).data)
            })

        return jsonify({"error": "Unknown statistics path"}), 404

    except grpc.RpcError as e:
        logging.error(f"gRPC Stats error: {e.code()}: {e.details()}")
        return jsonify({"error": "Failed to get stats"}), 500
    except Exception as e:
        logging.exception("Unexpected error")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
