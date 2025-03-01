from flask import Flask, request, jsonify
import requests
import logging
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

USERS_API_URL = os.environ.get('USERS_API_URL', 'http://auth:8090')
SECRET_KEY = os.environ.get('PRIVATE_KEY')

logging.basicConfig(level=logging.INFO)

def verify_token(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy(path):
    url = f"{USERS_API_URL}/{path}"
    # headers = {key: value for key, value in request.headers if key.lower() != "host"}

    logging.info(f"Forwarding {request.method} request to {url}")
    
    try:
        data = request.get_json(silent=True, force=True)
        if request.method == "GET":
            resp = requests.get(url, json=data, cookies=request.cookies)
        elif request.method == "POST":
            resp = requests.post(url, json=data, cookies=request.cookies)
        elif request.method == "PUT":
            resp = requests.put(url,  json=data, cookies=request.cookies)
        elif request.method == "DELETE":
            resp = requests.delete(url, json=data, cookies=request.cookies)
        
        return (resp.content, resp.status_code, resp.headers.items())
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
        return jsonify({"error": "Failed to connect to User Service API "}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
