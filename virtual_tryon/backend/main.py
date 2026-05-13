import os
import sys
import uuid
import datetime
import traceback
import requests
from fastapi import FastAPI, HTTPException, Depends, Header, File, UploadFile, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import mysql.connector
from dotenv import load_dotenv
import os

# Add parent directory to sys.path to allow importing ml_model
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


# Load environment variables from .env
load_dotenv(os.path.join(BASE_DIR, '.env'))

# MySQL connection setup using environment variables
MYSQL_CONFIG = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': os.getenv('MYSQL_HOST'),
    'database': os.getenv('MYSQL_DATABASE'),
    'raise_on_warnings': True
}

ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')

def get_mysql_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)

# Initialize FastAPI app
app = FastAPI(title="Virtual Try-On API (MySQL)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper to insert image and return its id
def insert_image(conn, user_id, img_type, filename):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO images (user_id, type, filename) VALUES (%s, %s, %s)",
        (user_id, img_type, filename)
    )
    conn.commit()
    img_id = cursor.lastrowid
    cursor.close()
    return img_id

# Helper to log activity
def log_activity(conn, user_id, action, details=None):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO activity_log (user_id, action, details) VALUES (%s, %s, %s)",
        (user_id, action, details)
    )
    conn.commit()
    cursor.close()

# User registration endpoint
@app.post("/register")
async def register_user(data: dict = Body(...)):
    email = data.get('email')
    password = data.get('password')
    name = data.get('name', None)
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    conn = get_mysql_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password, name) VALUES (%s, %s, %s)", (email, password, name))
        conn.commit()
        user_id = cursor.lastrowid
        log_activity(conn, user_id, 'register', f"User {email} registered.")
    except mysql.connector.IntegrityError:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=409, detail="Email already registered")
    cursor.close()
    conn.close()
    return {"message": "Registration successful"}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Mount the static directory so images can be served using the result_url
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Mount the results directory for serving generated try-on images
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)
app.mount("/results", StaticFiles(directory=RESULTS_DIR), name="results")

def get_current_user(authorization: str = Header(None)):
    # Simple MySQL-based authentication (for demo; use hashed passwords in production)
    if not authorization or not authorization.startswith("Basic "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    import base64
    try:
        auth_decoded = base64.b64decode(authorization.split("Basic ")[1]).decode()
        email, password = auth_decoded.split(":", 1)
    except Exception:
        raise HTTPException(status_code=401, detail="Malformed Basic Auth header")
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

@app.post("/try-on")
async def process_try_on(
    user_image: UploadFile = File(...),
    cloth_image: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """Endpoint to trigger the virtual try-on ML process from local file uploads."""
    user_img_path = os.path.join(UPLOAD_DIR, f"user_{uuid.uuid4().hex}_{user_image.filename}")
    cloth_img_path = os.path.join(UPLOAD_DIR, f"cloth_{uuid.uuid4().hex}_{cloth_image.filename}")

    with open(user_img_path, "wb") as f:
        f.write(await user_image.read())
    with open(cloth_img_path, "wb") as f:
        f.write(await cloth_image.read())

    try:
        from ml_model.model import process_virtual_tryon
        print(f"Processing try-on: {user_img_path}, {cloth_img_path}")
        # Save result in backend/results/
        output_filename = process_virtual_tryon(user_img_path, cloth_img_path, RESULTS_DIR)
        output_filepath = os.path.join(RESULTS_DIR, output_filename)
        print(f"ML process done. Saving to: {output_filepath}")
        conn = get_mysql_connection()
        # Insert images and get their IDs
        user_img_id = insert_image(conn, user['id'], 'user', os.path.basename(user_img_path))
        cloth_img_id = insert_image(conn, user['id'], 'cloth', os.path.basename(cloth_img_path))
        result_img_id = insert_image(conn, user['id'], 'result', output_filename)
        # Store result metadata in results table
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO results (user_id, user_image_id, cloth_image_id, result_image_id, created_at) VALUES (%s, %s, %s, %s, %s)",
            (user['id'], user_img_id, cloth_img_id, result_img_id, datetime.datetime.now())
        )
        conn.commit()
        cursor.close()
        # Log activity
        log_activity(conn, user['id'], 'try-on', f"Try-on with user_img_id={user_img_id}, cloth_img_id={cloth_img_id}, result_img_id={result_img_id}")
        conn.close()
        result_url = f"/results/{output_filename}"
        return JSONResponse(content={
            "message": "Try-on processed successfully",
            "output_image": output_filename,
            "result_url": result_url
        })
    except Exception as e:
        print(f"Exception during Try-on: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error processing try-on: {str(e)}")

@app.get("/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    return {
        "id": user['id'],
        "email": user['email'],
        "name": user.get('name'),
        "is_admin": user.get('is_admin', False)
    }

@app.get("/user/history")
async def get_user_history(user: dict = Depends(get_current_user)):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT r.*, i.filename 
        FROM results r 
        LEFT JOIN images i ON r.result_image_id = i.id 
        WHERE r.user_id = %s 
        ORDER BY r.created_at DESC
    ''', (user['id'],))
    history = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"history": history}

@app.get("/admin/users")
async def get_admin_users(user: dict = Depends(get_current_user)):
    """Endpoint to fetch all users (Admin only) - MySQL version."""
    if user.get('email') != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, email FROM users")
    users = cursor.fetchall()
    cursor.execute('''
        SELECT r.*, i.filename 
        FROM results r 
        LEFT JOIN images i ON r.result_image_id = i.id 
        ORDER BY r.created_at DESC
    ''')
    history = cursor.fetchall()
    cursor.close()
    conn.close()
    # Add tryon_count and last_active for each user
    user_map = {u['id']: {**u, 'tryon_count': 0, 'last_active': None} for u in users}
    for h in history:
        uid = h['user_id']
        if uid in user_map:
            user_map[uid]['tryon_count'] += 1
            if not user_map[uid]['last_active'] or h['created_at'] > user_map[uid]['last_active']:
                user_map[uid]['last_active'] = h['created_at']
    return JSONResponse(content={
        "users": list(user_map.values()),
        "history": history
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
