from flask import Flask, request, jsonify
import jwt
import datetime
import requests

app = Flask(__name__)

# CONFIGURATION
# ----------------
# INTENTIONAL VULNERABILITY: Hardcoded Secret Key
SECRET_KEY = "ground_station_secret_key_123"
# Point to NebulaX Core to log access attempts
CORE_API_URL = "http://nebulax-core:8000/events/ingest"

def log_event(event_type, severity, description, related_ip):
    """
    Sends logs to the NebulaX Core (Blue Team will see this!)
    """
    try:
        payload = {
            "event_meta": {
                "origin_module": "space.ground.sim",
                "event_type": event_type,
                "severity": severity,
                "classification": "SIMULATION"
            },
            "context": {
                "related_ip": related_ip,
                "related_asset_id": "GROUND-STATION-ALPHA"
            },
            "payload": {
                "message": description
            }
        }
        requests.post(CORE_API_URL, json=payload, timeout=2)
    except:
        pass # Fail silently if Core is down

@app.route('/')
def index():
    return jsonify({
        "system": "OrbitGuard Ground Station Alpha",
        "status": "ONLINE",
        "endpoints": [
            "/api/login",
            "/api/telemetry (Auth Required)",
            "/api/command (Auth Required)"
        ]
    })

@app.route('/api/login', methods=['POST'])
def login():
    """
    VULNERABILITY: Hardcoded Creds & No Rate Limiting.
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')
    ip = request.remote_addr

    # INTENTIONAL FLAW: Weak Credentials
    if username == 'admin' and password == 'solarwinds123':
        # Generate Token
        token = jwt.encode({
            'user': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, SECRET_KEY, algorithm="HS256")
        
        log_event("AUTH_SUCCESS", "INFO", f"User {username} logged in", ip)
        return jsonify({'token': token})
    
    log_event("AUTH_FAILURE", "LOW", f"Failed login attempt for {username}", ip)
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/telemetry', methods=['GET'])
def get_telemetry():
    """
    Returns mock satellite data.
    VULNERABILITY: IDOR / Token checking is weak.
    """
    token = request.headers.get('Authorization')
    
    if not token:
        return jsonify({'message': 'Token required'}), 403
    
    try:
        # Clean "Bearer <token>"
        if "Bearer " in token:
            token = token.split(" ")[1]
        
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        # Mock Data
        return jsonify({
            "sat_id": "NOAA-20",
            "battery_level": "84%",
            "uplink_frequency": "401.5 MHz",
            "status": "NOMINAL"
        })
    except Exception as e:
        return jsonify({'message': 'Invalid Token', 'error': str(e)}), 403

if __name__ == '__main__':
    print(" [ Ground Sim ] Listening on port 5000...")
    app.run(host='0.0.0.0', port=5000)