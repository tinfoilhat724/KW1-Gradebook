from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import json
import os

app = Flask(__name__)
# Use a secure secret key for sessions (can be an environment variable)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secure-command-password-here')

# Set your team's password here
APP_PASSWORD = os.environ.get('APP_PASSWORD', 'WTI-secure-2026')
DB_NAME = "gradebook.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_state (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('password') == APP_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = 'Invalid tactical password.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM app_state WHERE key = "main_data"')
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return jsonify(json.loads(row[0]))
    return jsonify({})

@app.route('/api/data', methods=['POST'])
def save_data():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO app_state (key, value) VALUES ('main_data', ?)
    ''', (json.dumps(data),))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)