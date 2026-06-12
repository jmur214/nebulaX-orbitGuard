from flask import Flask, request, redirect, url_for, session
import sqlite3
import requests
import os

app = Flask(__name__)
app.secret_key = "astra_dynamics_insecure_key"

# CONFIGURATION
# Use host.docker.internal to talk to Core
CORE_HOST = os.getenv("CORE_HOST", "nebulax-core")
CORE_API_URL = f"http://{CORE_HOST}:8000/events/ingest"

# IN-MEMORY DATABASE
def init_db():
    # --- FIX IS HERE: check_same_thread=False ---
    # This allows Flask's worker threads to access the global DB object
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    
    # Seed Data
    c.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'flag{astra_master_key_xyz}', 'admin')")
    c.execute("INSERT INTO users (username, password, role) VALUES ('guest', 'guest', 'user')")
    conn.commit()
    return conn

# Global connection (Now thread-safe enough for a lab)
db = init_db()

def log_traffic(endpoint, method, status, ip, payload_data=None):
    """
    Send traffic logs to NebulaX Core for Blue Team analysis
    """
    event = {
        "event_meta": {
            "origin_module": "target.public.web",
            "event_type": "WEB_TRAFFIC",
            "severity": "INFO",
            "classification": "SIMULATION"
        },
        "context": {
            "related_ip": ip,
            "related_asset_id": "ASTRA-WEB-01"
        },
        "payload": {
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "user_agent": request.headers.get('User-Agent'),
            "payload_snippet": str(payload_data)[:100] if payload_data else None
        }
    }
    try:
        requests.post(CORE_API_URL, json=event, timeout=1)
    except:
        pass

# --- VULNERABLE ROUTES ---

@app.route('/', methods=['GET'])
def home():
    log_traffic("/", "GET", 200, request.remote_addr)
    return """
    <style>
        body { background-color: #0f172a; color: #e2e8f0; font-family: monospace; text-align: center; padding-top: 50px; }
        h1 { color: #06b6d4; }
        .box { border: 1px solid #1e293b; display: inline-block; padding: 20px; margin-top: 20px; }
        input { display: block; margin: 10px auto; padding: 10px; width: 200px; background: #1e293b; border: 1px solid #334155; color: white; }
        button { background: #06b6d4; color: black; border: none; padding: 10px 20px; cursor: pointer; font-weight: bold; }
    </style>
    <h1>ASTRA DYNAMICS</h1>
    <p>SECURE PARTNER PORTAL</p>
    <div class="box">
        <form action="/login" method="POST">
            <input type="text" name="username" placeholder="Username">
            <input type="password" name="password" placeholder="Password">
            <button type="submit">AUTHENTICATE</button>
        </form>
    </div>
    """

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    ip = request.remote_addr

    # --- VULNERABILITY: SQL INJECTION ---
    # We are formatting the string directly into the query.
    # An attacker can enter: admin' --
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    
    try:
        cursor = db.cursor()
        cursor.execute(query) # EXECUTING RAW STRING
        user = cursor.fetchone()

        if user:
            session['user'] = user[1]
            session['role'] = user[3]
            log_traffic("/login", "POST", 200, ip, f"Auth Success: {username}")
            return redirect(url_for('dashboard'))
        else:
            log_traffic("/login", "POST", 401, ip, f"Failed Query: {query}")
            return "<h1>ACCESS DENIED</h1><a href='/'>Try Again</a>", 401

    except Exception as e:
        log_traffic("/login", "POST", 500, ip, f"SQL Error: {str(e)}")
        return f"<h1>DATABASE ERROR</h1><p>{e}</p>", 500

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('home'))
    
    log_traffic("/dashboard", "GET", 200, request.remote_addr)
    
    flag = "LOCKED"
    if session.get('role') == 'admin':
        flag = "ASTRA_SECRET_PROJECT_ORION_BLUEPRINTS.PDF"

    return f"""
    <style>body {{ background-color: #0f172a; color: #e2e8f0; font-family: monospace; padding: 50px; }}</style>
    <h1>WELCOME, {session['user'].upper()}</h1>
    <p>ROLE: {session['role']}</p>
    <hr>
    <h3>INTERNAL DOCUMENTS</h3>
    <ul>
        <li>Employee Handbook (Public)</li>
        <li>Cafeteria Menu (Public)</li>
        <li style="color: #ef4444;">{flag}</li>
    </ul>
    """

if __name__ == '__main__':
    # Listen on all interfaces (0.0.0.0) so Docker can map the port
    app.run(host='0.0.0.0', port=5000)