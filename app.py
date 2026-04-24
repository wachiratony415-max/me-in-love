from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
import os

app = Flask(__name__)

# ── SECRET KEY ──
# Must be a fixed string — never random/generated on startup.
# If it changes between Render restarts, all sessions are wiped.
app.secret_key = os.environ.get('SECRET_KEY', 'tony-loves-ella-forever-2024-fixed')

# ── SESSION / COOKIE CONFIG ──
# These settings make cookies work correctly on ALL Android versions,
# old WebViews (Android 6, 7), and all browsers.
app.config['SESSION_COOKIE_HTTPONLY']  = True       # JS can't steal the cookie
app.config['SESSION_COOKIE_SAMESITE']  = 'Lax'      # Best compatibility across old/new browsers
app.config['SESSION_COOKIE_SECURE']    = False       # Set True ONLY if your site uses HTTPS everywhere
app.config['SESSION_COOKIE_NAME']      = 'tonyella'  # Custom name avoids conflicts with other Flask apps
app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24 * 30  # Session lasts 30 days (in seconds)


# ── ACCEPTED CREDENTIALS ──
VALID_NAMES = {'ella', 'stella', 'stela'}
VALID_CODE  = 'LOVE'


# ── LOGIN REQUIRED DECORATOR ──
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            # Clear any broken/partial session before redirecting
            session.clear()
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ── LOGIN PAGE ──
@app.route('/', methods=['GET'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    return render_template('login.html')


# ── LOGIN POST (AJAX) ──
@app.route('/login', methods=['POST'])
def do_login():
    # Handle both JSON and form data — some old Android browsers
    # send form-encoded data instead of JSON
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict()

    name     = data.get('name', '').strip().lower()
    password = data.get('password', '').strip()

    if name in VALID_NAMES and password == VALID_CODE:
        # Make the session permanent so it survives browser restarts
        session.permanent = True
        session['logged_in'] = True
        session['user_name']  = name.capitalize()
        # Force the session to be written immediately
        session.modified = True
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Only Ella can enter 💔'})


# ── DASHBOARD ──
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=session.get('user_name', 'Ella'))


# ── LOGOUT ──
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ── SESSION CHECK (used by JS to verify session is alive) ──
# Call this from JS if you ever need to silently check login status
@app.route('/session-check')
def session_check():
    if session.get('logged_in'):
        return jsonify({'logged_in': True, 'user': session.get('user_name')})
    return jsonify({'logged_in': False})


if __name__ == '__main__':
    app.run(debug=False)  # debug=False is safer and avoids reloader wiping sessions
