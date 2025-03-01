from flask import Flask, request, jsonify, make_response
import jwt
import datetime
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from marshmallow import Schema, fields, ValidationError
import logging
from email_validator import validate_email, EmailNotValidError

load_dotenv()

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

private_key = os.getenv("PRIVATE_KEY")
public_key = os.getenv("PUBLIC_KEY")

def get_db_connection():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        cursor_factory=RealDictCursor
    )
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_profiles (
            profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            phone_number VARCHAR(20),
            birthdate DATE,
            bio TEXT
        );

        CREATE TABLE IF NOT EXISTS user_roles (
            role_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            role_name VARCHAR(20) NOT NULL,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        );

        CREATE TABLE IF NOT EXISTS sessions (
            session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            token TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

class ProfileSchema(Schema):
    first_name = fields.String()
    last_name = fields.String()
    birth_date = fields.Date()
    email = fields.Email()  
    phone_number = fields.String()
    bio = fields.String()


class RoleSchema(Schema):
    role_name = fields.String(required=True)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json(force=True)
    if not data or 'username' not in data or 'password' not in data or 'email' not in data:
        return make_response("Missing required fields", 400)

    username = data['username']
    password = str(data['password'])
    email = data['email']
    
    try:
        emailinfo = validate_email(email, check_deliverability=False)
        email = emailinfo.normalized
    except EmailNotValidError as e:
        return make_response(str(e), 400)
    
    hashed_password = generate_password_hash(password)

    try:
        init_db()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (username, email, password_hash) 
            VALUES (%s, %s, %s)
        """, (username, email, hashed_password))
        conn.commit()
        cur.close()
        conn.close()
    except psycopg2.IntegrityError:
        return make_response("User already exists", 403)

    token = jwt.encode({'username': username, 'iat': datetime.datetime.utcnow()}, private_key, algorithm='RS256')
    response = make_response("", 200)
    response.set_cookie('jwt', token)
    return response

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    if not data or 'username' not in data or 'password' not in data:
        return make_response("Missing required fields", 400)

    username = data['username']
    password = data['password']
    
    try:
        init_db()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id, password_hash FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
    except:
        return make_response("User not found", 404)
    
    if not user or not check_password_hash(user['password_hash'], password):
        cur.close()
        conn.close()
        return make_response("Invalid credentials", 403)
    
    user_id = user['user_id']
    token = jwt.encode({'username': username, 'iat': datetime.datetime.utcnow()}, private_key, algorithm='RS256')
    
    try:
        cur.execute("""
            INSERT INTO sessions (user_id, created_at, token)
            VALUES (%s, %s, %s)
        """, (user_id, datetime.datetime.utcnow(), token))
        conn.commit()
        cur.close()
        conn.close()
    except psycopg2.IntegrityError:
        cur.close()
        conn.close()
        return make_response("Session already exists", 409)

    response = make_response("", 200)
    response.set_cookie('jwt', token)
    return response

@app.route('/profile', methods=['GET'])
def get_profile():
    token = request.cookies.get('jwt')
    if not token:
        return make_response("Missing or invalid token\n", 401)
    try:
        decoded = jwt.decode(token, public_key, algorithms=['RS256'])
        username = decoded['username']
    except jwt.ExpiredSignatureError:
        return make_response("Token expired\n", 400)
    except jwt.InvalidTokenError:
        return make_response("Invalid token\n", 400)
    if not username:
        return make_response("Unauthorized", 403)

    try:
        init_db()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT u.username, u.email, u.created_at, p.phone_number, 
                p.first_name, p.last_name, p.birthdate, p.bio 
            FROM users u 
            LEFT JOIN user_profiles p ON u.user_id = p.user_id 
            WHERE u.username = %s
        """, (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
    except:
        return make_response("User not found", 404)

    return jsonify(user)

@app.route('/profile', methods=['PUT'])
def update_profile():
    token = request.cookies.get('jwt')
    if not token:
        return make_response("Missing or invalid token\n", 401)
    try:
        decoded = jwt.decode(token, public_key, algorithms=['RS256'])
        username = decoded['username']
    except jwt.ExpiredSignatureError:
        return make_response("Token expired\n", 400)
    except jwt.InvalidTokenError:
        return make_response("Invalid token\n", 400)
    if not username:
        return make_response("Unauthorized", 403)
    
    try:
        data = ProfileSchema().load(request.get_json(force=True))
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    fields_to_update = ', '.join(f"{key} = %s" for key in data.keys())
    values = list(data.values()) + [username]

    try:
        init_db()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"""
            INSERT INTO user_profiles (user_id, {', '.join(data.keys())})
            VALUES ((SELECT user_id FROM users WHERE username = %s), {', '.join(['%s'] * len(data))})
            ON CONFLICT (user_id) DO UPDATE SET {fields_to_update}
        """, [username] + values)
        conn.commit()
        cur.close()
        conn.close()
    except psycopg2.IntegrityError:
        cur.close()
        conn.close()
        return make_response("Error occured while updating profile", 409)
    
    return make_response("Profile updated", 200)


@app.route('/roles', methods=['POST'])
def assign_role():
    token = request.cookies.get('jwt')
    if not token:
        return make_response("Missing or invalid token", 401)
    try:
        decoded = jwt.decode(token, public_key, algorithms=['RS256'])
        username = decoded['username']
    except jwt.ExpiredSignatureError:
        return make_response("Token expired", 400)
    except jwt.InvalidTokenError:
        return make_response("Invalid token", 400)
    
    try:
        data = RoleSchema().load(request.get_json(force=True))
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    try:
        init_db()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
        SELECT 1 FROM user_roles 
        WHERE user_id = (SELECT user_id FROM users WHERE username = %s) 
        AND role_name = %s
        """, (username, data['role_name']))

        if cur.fetchone():
            raise psycopg2.IntegrityError
        
        cur.execute("""
                INSERT INTO user_roles (user_id, role_name)
                VALUES ((SELECT user_id FROM users WHERE username = %s), %s)
        """, (username, data['role_name']))
        conn.commit()
        cur.close()
        conn.close()
    except psycopg2.IntegrityError:
        cur.close()
        conn.close()
        return make_response("Role already assigned", 409)
    
    return make_response("Role assigned", 200)

@app.route('/roles', methods=['GET'])
def get_roles():
    token = request.cookies.get('jwt')
    if not token:
        return make_response("Missing or invalid token", 401)
    try:
        decoded = jwt.decode(token, public_key, algorithms=['RS256'])
        username = decoded['username']
    except jwt.ExpiredSignatureError:
        return make_response("Token expired", 400)
    except jwt.InvalidTokenError:
        return make_response("Invalid token", 400)
    
    try:
        init_db()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT role_name, assigned_at, is_active FROM user_roles
            WHERE user_id = (SELECT user_id FROM users WHERE username = %s)
        """, (username,))
        roles = cur.fetchall()
        cur.close()
        conn.close()
    except:
        return make_response("User not found", 404)
    
    return jsonify(roles)

@app.route('/roles', methods=['DELETE'])
def delete_role():
    token = request.cookies.get('jwt')
    if not token:
        return make_response("Missing or invalid token", 401)
    
    try:
        decoded = jwt.decode(token, public_key, algorithms=['RS256'])
        username = decoded['username']
    except jwt.ExpiredSignatureError:
        return make_response("Token expired", 400)
    except jwt.InvalidTokenError:
        return make_response("Invalid token", 400)

    try:
        data = RoleSchema().load(request.get_json(force=True))
    except ValidationError as err:
        return jsonify(err.messages), 400

    try:
        init_db()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM user_roles 
            WHERE user_id = (SELECT user_id FROM users WHERE username = %s)
            AND role_name = %s
        """, (username, data['role_name']))
        
        if cur.rowcount == 0:
            cur.close()
            conn.close()
            return make_response("Role not found", 404)

        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logging.error(f"Error while deleting role: {e}")
        return make_response("Error occurred while deleting role", 400)

    return make_response("Role deleted", 200)


@app.route('/sessions', methods=['GET'])
def get_sessions():
    token = request.cookies.get('jwt')
    if not token:
        return make_response("Missing or invalid token", 401)
    try:
        decoded = jwt.decode(token, public_key, algorithms=['RS256'])
        username = decoded['username']
    except jwt.ExpiredSignatureError:
        return make_response("Token expired", 400)
    except jwt.InvalidTokenError:
        return make_response("Invalid token", 400)
    
    try:
        init_db()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT session_id, created_at FROM sessions
            WHERE user_id = (SELECT user_id FROM users WHERE username = %s)
        """, (username,))
        sessions = cur.fetchall()
        cur.close()
        conn.close()
    except:
        return make_response("User not found", 404)
    
    return jsonify(sessions)

@app.route('/logout', methods=['DELETE'])
def logout_session():
    token = request.cookies.get('jwt')
    if not token:
        return make_response("Missing or invalid token", 401)
    try:
        decoded = jwt.decode(token, public_key, algorithms=['RS256'])
        username = decoded['username']
    except jwt.ExpiredSignatureError:
        return make_response("Token expired", 400)
    except jwt.InvalidTokenError:
        return make_response("Invalid token", 400)
    
    json = request.get_json(force=True)
    
    try:
        init_db()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM sessions WHERE session_id = %s AND user_id = (SELECT user_id FROM users WHERE username = %s)
        """, (json["session_id"], username))
        conn.commit()
        cur.close()
        conn.close()
    except:
        return make_response("Error occured while logging out session", 400)
    
    return make_response("Session logged out", 200)

@app.route("/drop_tables", methods=["DELETE"])
def drop_tables():
    # logging.warning("Drop tables")
    token = request.cookies.get('jwt')
    if not token:
        return make_response("Missing or invalid token", 401)
    try:
        decoded = jwt.decode(token, public_key, algorithms=['RS256'])
        username = decoded['username']
        # logging.warning(f"{username}")
    except jwt.ExpiredSignatureError:
        return make_response("Token expired", 400)
    except jwt.InvalidTokenError:
        return make_response("Invalid token", 400)
    
    json = request.get_json(force=True)
    
    try:
        tables = json["tables"]
        logging.warning(f"{tables}")
    except KeyError:
        return make_response("Missing 'tables' field in request body", 400)
    
    try:
        init_db()
        conn = get_db_connection()
        cur = conn.cursor()
        
        for table in tables:
            cur.execute(f"""DROP TABLE IF EXISTS {table} CASCADE""")
        
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        return make_response("Error occured while deleteing tables", 400)
    
    return make_response("Tables deleted successfully", 200)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)
