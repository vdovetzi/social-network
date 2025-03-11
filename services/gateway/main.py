from flask import Flask, request, jsonify
import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

USERS_API_URL = os.environ.get('USERS_API_URL', 'http://auth:8090')
POSTS_API_URL = os.environ.get('POSTS_API_URL',  'http://posts:8091')
STATS_API_URL = os.environ.get('STATS_API_URL',   'http://stats:8092')


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

@app.route("/posts/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_posts(path):
    pass

@app.route("/stats/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_stats(path):
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
