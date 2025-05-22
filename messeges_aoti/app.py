import os
# Allow OAuth over HTTP for local development.
# WARNING: This is for development ONLY and should NOT be used in production.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from flask import Flask, render_template, request, redirect, url_for, flash, session, Blueprint
import toml # For reading secret.toml
import json
from requests_oauthlib import OAuth2Session
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleAuthRequest # Alias to avoid conflict with Flask's request
import sqlite3

# Ensure we are importing from the correct location relative to app.py
from .message_saver import (
    get_all_messages, save_message, create_user, get_user_by_email, get_user_by_google_id,
    _print_messages_for_cli, _ensure_tables_exist, get_all_users
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Blueprint("messeges_aoti", __name__, template_folder="./templates", url_prefix="/messeges_aoti")
app.html_name = "אוטי 2.0"
app.description = "אתר המשך לאפליקצה שכבר קיימת אוטי, \n האפליקציה היא בינה מלאכותית שנעזרת במשיבים אנושיים כדי לשפר את התשובות שלה"
app.html_creator = "רז"
app.html_link = "https://www.facebook.com/groups/1188234756236379/user/1051257580"
app.html_img = "/static/raz.jpg"



@app.route('/debug')
def debug():
    """דף דיבאג שמציג מידע על הסביבה הנוכחית"""
    current_url = request.host_url.rstrip('/')
    return f"Base Directory: {os.path.dirname(os.path.abspath(__file__))}<br>Current URL: {current_url}"


# --- Configuration from secret.toml ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_FILE_PATH = os.path.join(BASE_DIR, "secret.toml")
DB_NAME = "chat_history.db"
DB_PATH = os.path.join(BASE_DIR, DB_NAME)


secrets = toml.load(SECRET_FILE_PATH)
app.secret_key = secrets.get("FLASK_SECRET_KEY", "default_fallback_secret_key_for_dev")
GOOGLE_CLIENT_ID = secrets.get("CLIENT_ID")
GOOGLE_CLIENT_SECRET = secrets.get("CLIENT_SECRET")


# ---- ADD DIAGNOSTIC PRINTS ----
print(f"DEBUG: Attempting to load secrets from: {SECRET_FILE_PATH}")
print(f"DEBUG: Loaded FLASK_SECRET_KEY: {app.secret_key}")
print(f"DEBUG: Loaded GOOGLE_CLIENT_ID: {GOOGLE_CLIENT_ID}")
print(f"DEBUG: Loaded GOOGLE_CLIENT_SECRET: {GOOGLE_CLIENT_SECRET}")
# ---- END DIAGNOSTIC PRINTS ----

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    print("Warning: Google Client ID or Secret is not configured. Google login will not work.")

# --- Google OAuth2 Configuration ---
AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
TOKEN_URL = 'https://oauth2.googleapis.com/token'
USERINFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'

SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]

# Ensure the directory for the DB exists when the app starts
os.makedirs(BASE_DIR, exist_ok=True)

# Helper functions for login/session management
def login_user_session(user_db_record):
    """Store user info in session"""
    session['user_id'] = user_db_record['id'] 
    session['username'] = user_db_record['username']
    session['email'] = user_db_record['email']
    session['logged_in'] = True

def logout_user_session():
    """Remove user info from session"""
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('email', None)
    session.pop('logged_in', None)
    session.pop('oauth_state', None) # Clear OAuth state too
    session.pop('oauth_token', None)

def get_current_user_from_session():
    """Get current logged-in user info from session"""
    if 'logged_in' in session and session['logged_in']:
        return {
            'id': session.get('user_id', 0),
            'username': session.get('username', 'Anonymous'),
            'email': session.get('email', '')
        }
    return None


@app.route('/', methods=['GET', 'POST'])
def index():
    # Get current user info, if any
    current_user = get_current_user_from_session()
    
    if request.method == 'POST':
        message_content = request.form.get('message')
        if message_content:
            # Use user_id from session if user is logged in, otherwise use 0
            user_id_to_save = current_user['id'] if current_user else 0
            save_message(message_content, user_id=user_id_to_save, db_path=DB_PATH)
            flash('Message saved successfully!', 'success')
        return redirect(url_for('messeges_aoti.index'))

    # For GET request, or after POST redirect
    messages = get_all_messages(db_path=DB_PATH)
    return render_template('messeges_aoti/templates/messages.html', messages=messages, user=current_user)

@app.route('/admin', methods=['GET'])
def admin():
    users = get_all_users(db_path=DB_PATH)
    return render_template('messeges_aoti/templates/users.html', users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if get_current_user_from_session():
        return redirect(url_for('messeges_aoti.index'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please provide both email and password', 'error')
            return render_template('login.html')
        
        user = get_user_by_email(email, db_path=DB_PATH)
        
        if user and user.get('password_hash') and check_password_hash(user['password_hash'], password):
            login_user_session(user)
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('messeges_aoti.index'))
        else:
            flash('Invalid email or password. Please try again or register.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if get_current_user_from_session():
        return redirect(url_for('messeges_aoti.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not username or not email or not password:
            flash('Please fill in all fields', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        existing_user = get_user_by_email(email, db_path=DB_PATH)
        if existing_user:
            flash('Email already registered. Please log in.', 'error')
            return redirect(url_for('messeges_aoti.login'))
        
        # Hash the password for security
        password_hash = generate_password_hash(password)
        
        # Create the user
        user_id = create_user(username, email, password_hash=password_hash, db_path=DB_PATH)
        
        if user_id:
            # Get the user info
            user = get_user_by_email(email, db_path=DB_PATH)
            login_user_session(user)  # Log them in automatically
            flash(f'Account created successfully. Welcome, {username}!', 'success')
            return redirect(url_for('messeges_aoti.index'))
        else:
            flash('An error occurred during registration', 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user_session()
    flash('You have been logged out.', 'info')
    return redirect(url_for('messeges_aoti.index'))

# --- Google OAuth Routes ---
@app.route('/login/google')
def google_login_request():
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        flash('Google login is not configured on the server.', 'error')
        return redirect(url_for('messeges_aoti.login'))

    # קבלת כתובת ה-redirect URI באמצעות request.host_url
    current_url = request.host_url.rstrip('/')  # מסיר את הסלאש בסוף אם קיים
    redirect_uri = f"{current_url}/login/google/callback"
    
    google = OAuth2Session(GOOGLE_CLIENT_ID, scope=SCOPES, redirect_uri=redirect_uri)
    authorization_url, state = google.authorization_url(AUTHORIZATION_URL, access_type="offline", prompt="select_account")
    
    # שמירת המידע בסשן
    session['oauth_state'] = state  # שמירת ה-state להגנה מפני CSRF
    session['redirect_uri'] = redirect_uri  # שמירת כתובת ה-redirect לשימוש בקריאת חזרה
    
    # הדפסת מידע לדיבאג
    print(f"DEBUG: Redirect URI set to: {redirect_uri}")
    
    return redirect(authorization_url)

@app.route('/login/google/callback')
def google_login_callback():
    return handle_google_callback()

def handle_google_callback():
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        flash('Google login is not configured on the server (callback).', 'error')
        return redirect(url_for('messeges_aoti.login'))

    # CSRF protection: check state
    state_from_session = session.pop('oauth_state', None)
    state_from_request = request.args.get('state')
    if not state_from_session or state_from_session != state_from_request:
        flash('Invalid OAuth state. Please try logging in again.', 'error')
        return redirect(url_for('messeges_aoti.login'))

    # קבלת כתובת ה-redirect מהסשן, או יצירה מחדש אם לא קיימת
    redirect_uri = session.get('redirect_uri')
    if not redirect_uri:
        current_url = request.host_url.rstrip('/')
        redirect_uri = f"{current_url}/login/google/callback"
        print(f"WARNING: redirect_uri not found in session, recreated as: {redirect_uri}")
    
    google = OAuth2Session(GOOGLE_CLIENT_ID, redirect_uri=redirect_uri, state=state_from_session)
    
    try:
        # Exchange authorization code for tokens
        token = google.fetch_token(TOKEN_URL, client_secret=GOOGLE_CLIENT_SECRET, authorization_response=request.url)
        session['oauth_token'] = token # Store the token (optional, for future API calls)

        # Get user info from Google
        userinfo_response = google.get(USERINFO_URL)
        if not userinfo_response.ok:
            flash('Failed to fetch user info from Google.', 'error')
            return redirect(url_for('messeges_aoti.login'))
        
        user_info_json = userinfo_response.json()
        google_id = user_info_json.get('id')
        email = user_info_json.get('email')
        username = user_info_json.get('name') or user_info_json.get('given_name') or email.split('@')[0]

        if not email or not google_id:
            flash('Could not retrieve email or Google ID from Google.', 'error')
            return redirect(url_for('messeges_aoti.login'))

        # Check if user exists by Google ID or email, then create/update
        user = get_user_by_google_id(google_id, db_path=DB_PATH)
        if not user:
            user = get_user_by_email(email, db_path=DB_PATH)
            if user: # User exists by email, link Google ID
                if not user.get('google_id'):
                    # This update logic is better placed within create_user or a dedicated update function
                    # For now, we assume create_user handles this if it finds by email and google_id is new.
                    pass # create_user will attempt to link or return existing if google_id matches
            
        if not user: # Still no user, create a new one
            user_id = create_user(username, email, google_id=google_id, db_path=DB_PATH)
            if user_id:
                user = get_user_by_google_id(google_id, db_path=DB_PATH) # Fetch the newly created user
            else:
                flash('Failed to create or link your account.', 'error')
                return redirect(url_for('messeges_aoti.login'))
        else: # User found, ensure their username is up-to-date from Google if needed
            if user['username'] != username: # Trivial update example
                 # Potentially update username or other details here in DB
                 pass # For simplicity, not doing DB write here, create_user logic is primary

        if user:
            login_user_session(user)
            flash(f'Successfully logged in as {user["username"]} via Google!', 'success')
            return redirect(url_for('messeges_aoti.index'))
        else:
            flash('An unexpected error occurred during Google login.', 'error')
            return redirect(url_for('messeges_aoti.login'))

    except Exception as e:
        flash(f'Google login failed: {str(e)}', 'error')
        print(f"Google OAuth Error: {e}") # Log the error for debugging
        return redirect(url_for('messeges_aoti.login'))

if __name__ == '__main__':
    print(f"Database will be accessed at: {DB_PATH}")
    if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
        print(f"Google OAuth configured. CLIENT_ID: {GOOGLE_CLIENT_ID[:10]}...")
    else:
        print("Google OAuth NOT CONFIGURED. Google login will fail.")

    # Startup DB check and CLI print (from message_saver)
    conn_startup = sqlite3.connect(DB_PATH)
    cursor_startup = conn_startup.cursor()
    _ensure_tables_exist(cursor_startup) # from message_saver, ensures tables are there
    conn_startup.commit()
    conn_startup.close()
    
    print("Initial messages in database (CLI for startup verification):")
    initial_messages = get_all_messages(db_path=DB_PATH)
    _print_messages_for_cli(initial_messages)

    app.run(debug=True, host='0.0.0.0', port=5001) # Using port 5001 to avoid common conflicts 