from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
import os
from authlib.integrations.flask_client import OAuth
from functools import wraps
from datetime import datetime

from .models import db, User  # ← ONLY import models this way

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = (
    "sqlite:///" + os.path.join(BASE_DIR, "app.db")
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# In-memory storage
motion_settings = {}

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ---------------- ROUTES ---------------- #

@app.route('/')
def index():
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login'))

    username = session.get('user_name', user_email.split('@')[0])
    motion_enabled = motion_settings.get(user_email, True)

    return render_template(
        'index.html',
        pubnub_publish_key=os.environ.get('PUBNUB_PUBLISH_KEY'),
        pubnub_subscribe_key=os.environ.get('PUBNUB_SUBSCRIBE_KEY'),
        username=username,
        motion_enabled=motion_enabled
    )

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/api/motion/toggle', methods=['POST'])
def toggle_motion():
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.get_json()
    enabled = data.get('enabled', True)
    motion_settings[user_email] = enabled

    return jsonify(success=True, enabled=enabled)

@app.route('/api/user/settings')
def get_user_settings():
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({'error': 'Not logged in'}), 401

    return jsonify(
        name=session.get('user_name', 'User'),
        email=user_email,
        motion_enabled=motion_settings.get(user_email, True),
        last_login=datetime.now().isoformat()
    )

@app.route('/health')
def health():
    return jsonify(status='healthy', timestamp=datetime.now().isoformat())

@app.route('/google-login')
def google_login():
    redirect_uri = url_for('auth_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/callback')
def auth_callback():
    try:
        token = google.authorize_access_token()
        resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')
        user_info = resp.json()

        user = User.query.filter_by(email=user_info['email']).first()

        if not user:
            user = User(
                google_id=user_info['sub'],
                email=user_info['email'],
                name=user_info.get('name'),
                picture=user_info.get('picture')
            )
            db.session.add(user)
            db.session.commit()

        session['user_email'] = user.email
        session['user_name'] = user.name

        return redirect(url_for('index'))

    except Exception as e:
        app.logger.error(f"Google login failed: {e}")
        return render_template('login_error.html'), 401
