from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev")

# Simple in-memory user storage (for now)
users_db = {}
motion_settings = {}

# Routes
@app.route('/')
def index():
    # Check if user is logged in via session
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
    # For now, auto-login with a test user
    # In production, replace with Google OAuth
    session['user_email'] = 'test@example.com'
    session['user_name'] = 'Test User'
    return redirect(url_for('index'))

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
    
    return jsonify({
        'success': True,
        'enabled': enabled,
        'message': f'Motion detection {"enabled" if enabled else "disabled"}'
    })

@app.route('/api/user/settings')
def get_user_settings():
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({'error': 'Not logged in'}), 401
    
    return jsonify({
        'name': session.get('user_name', 'User'),
        'email': user_email,
        'motion_enabled': motion_settings.get(user_email, True),
        'last_login': datetime.now().isoformat()
    })

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

# Add a test route to verify it's working
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })