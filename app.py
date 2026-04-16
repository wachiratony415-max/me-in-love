from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps

app = Flask(__name__)
app.secret_key = 'tony-loves-ella-forever-2024'  # Change this to something secret in production

# ── ACCEPTED CREDENTIALS ──
VALID_NAMES = {'ella', 'stella', 'stela'}
VALID_CODE  = 'LOVE'


# ── LOGIN REQUIRED DECORATOR ──
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
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
    data     = request.get_json()
    name     = data.get('name', '').strip().lower()
    password = data.get('password', '').strip()

    if name in VALID_NAMES and password == VALID_CODE:
        session['logged_in'] = True
        session['user_name'] = name.capitalize()
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


if __name__ == '__main__':
    app.run(debug=True)
