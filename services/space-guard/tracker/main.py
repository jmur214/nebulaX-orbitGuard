import time
import json
import requests
import schedule
import os
import io
import base64
import random
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from skyfield.api import Topos, load, wgs84, utc
from datetime import datetime, timedelta

# CONFIGURATION
CORE_HOST = os.getenv("CORE_HOST", "nebulax-core")
CORE_API_URL = f"http://{CORE_HOST}:8000/events/ingest"
# Chicago Coordinates
GROUND_STATION = Topos('41.8952 N', '87.8257 W')

# SPACE-TRACK CREDENTIALS
ST_USER = os.getenv("ST_USER", "jsm13700@gmail.com")
ST_PASS = os.getenv("ST_PASS", "alalalal11221122")
ST_BASE = "https://www.space-track.org"

print(" [ OrbitGuard ] Satellite Tracking System Online...")

# 1. Load Data
eph = load('de421.bsp')
earth = eph['earth']

def fetch_spacetrack_metadata(sat_objects):
    """
    Fetches SATCAT metadata for a list of Skyfield satellite objects.
    """
    if not sat_objects: return {}
    
    session = requests.Session()
    # Login Flow
    try:
        resp = session.post(f"{ST_BASE}/ajaxauth/login", data={"identity": ST_USER, "password": ST_PASS}, timeout=10)
        if resp.status_code != 200: return {}
    except: return {}

    # Extract IDs
    norad_ids = [str(sat.model.satnum) for sat in sat_objects]
    # Chunking (SpaceTrack might limit URL length)
    chunk_size = 50
    metadata_map = {}
    
    import math
    chunks = [norad_ids[i:i + chunk_size] for i in range(0, len(norad_ids), chunk_size)]
    
    print(f" [ SpaceTrack ] Fetching Metadata for {len(norad_ids)} sats in {len(chunks)} chunks...")

    for chunk in chunks:
        try:
            id_str = ",".join(chunk)
            cat_resp = session.get(f"{ST_BASE}/basicspacedata/query/class/satcat/NORAD_CAT_ID/{id_str}/format/json")
            if cat_resp.status_code == 200:
                cat_data = cat_resp.json()
                for item in cat_data:
                    country = item.get('COUNTRY', 'UNK')
                    if country == 'US': country = 'USA'
                    elif country == 'PRC': country = 'CHINA'
                    elif country in ['CIS', 'RUS']: country = 'RUSSIA'
                    elif country == 'ESA': country = 'ESA'
                    
                    metadata_map[int(item['NORAD_CAT_ID'])] = {
                        "country": country,
                        "launch_year": item['LAUNCH'][:4] if item.get('LAUNCH') else "UNK",
                        "rcs_size": item.get('RCS_SIZE', 'UNK'),
                        "object_name": item.get('SATNAME', 'UNK')
                    }
        except Exception as e:
            print(f"[!] Metadata Fetch Error: {e}")
            
    return metadata_map

def fetch_spacetrack_tles():
    """
    Fetches high-interest TLEs (Favorites + Large Objects).
    """
    session = requests.Session()
    try:
        session.post(f"{ST_BASE}/ajaxauth/login", data={"identity": ST_USER, "password": ST_PASS}, timeout=10)
        
        favorites_ids = "25544,20580,43013,25994,27424" # ISS, HST, NOAA 20, TERRA, AQUA
        tles_fav = session.get(f"{ST_BASE}/basicspacedata/query/class/gp/NORAD_CAT_ID/{favorites_ids}/ORDINAL/1/EPOCH/%3Enow-30/format/tle").text
        
        # Reduced limit to ensure success
        tles_large = session.get(f"{ST_BASE}/basicspacedata/query/class/gp/RCS_SIZE/LARGE/DECAY/null/limit/30/orderby/LAUNCH_DATE%20desc/format/tle").text
        
        full_tle_text = tles_fav + "\n" + tles_large
        import io
        return load.tle_file(io.StringIO(full_tle_text))
    except:
        return []

# Execute Data Load Strategy
print(" [ OrbitGuard ] Initializing Satellite Database...")
active_sats = fetch_spacetrack_tles()

if not active_sats:
    print("[!] SpaceTrack TLE Fetch Failed. Falling back to Celestrak...")
    stations_list = load.tle_file(url='https://celestrak.org/NORAD/elements/stations.txt', reload=False)
    # Only load stations to keep it fast if API fails
    active_sats = stations_list

# ALWAYS try to fetch metadata, even for Celestrak data
sat_metadata = fetch_spacetrack_metadata(active_sats)
print(f" [ OrbitGuard ] Metadata loaded for {len(sat_metadata)} IDs.")

satellites = {sat.name: sat for sat in active_sats}

# Define Priority Targets (Cool Satellites) - These names must match what SpaceTrack returns or partial match
PRIORITY_TARGETS = ["ISS", "HST", "NOAA", "TERRA", "AQUA", "SUZAKU", "TIANGONG", "CSS"] # CSS = Chinese Space Station
final_target_name = "ISS (ZARYA)" # Default

# Global State
CLASSIFIER_MODEL = None
SATELLITE_DATA_CACHE = {}

# Space War Detector Integration
from war_detector.detector import SpaceWarDetector
WAR_DETECTOR = SpaceWarDetector()


# --- Helper Functions ---

def compute_orbital_parameters(sat):
    """
    Extracts orbital parameters from a Skyfield satellite object.
    """
    try:
        model = sat.model
        return {
            "inclination": model.inclo * 180.0 / 3.14159, 
            "eccentricity": model.ecco,
            "semi_major_axis": model.a * 6378.137, 
            "apogee": (model.a * (1 + model.ecco) - 1) * 6378.137, 
            "perigee": (model.a * (1 - model.ecco) - 1) * 6378.137, 
            "period_minutes": 2 * 3.14159 * (model.a * 6378.137)**1.5 / 398600.4418**0.5 / 60
        }
    except Exception:
        return { "inclination": 0, "eccentricity": 0, "semi_major_axis": 0, "apogee": 0, "perigee": 0, "period_minutes": 0}

def train_classifier(sat_dict, metadata_map):
    """
    Trains RandomForest using REAL Ground Truth from Space-Track.
    """
    data = []
    
    for sat in sat_dict.values():
        try:
            norad_id = sat.model.satnum
            params = compute_orbital_parameters(sat)
            
            # Ground Truth from Metadata
            truth = "UNKNOWN"
            if norad_id in metadata_map:
                truth = metadata_map[norad_id]["country"]
            else:
                # Fallback heuristic if metadata missing (unlikely if API worked)
                name = sat.name.upper()
                if "US" in name or "NOAA" in name: truth = "USA"
                elif "COSMOS" in name: truth = "RUSSIA"
            
            if truth != "UNKNOWN":
                data.append({
                    "inclination": params["inclination"],
                    "apogee": params["apogee"],
                    "country": truth
                })
        except:
            continue
    
    df = pd.DataFrame(data)
    if len(df) < 5:
        print("[!] Not enough data for ML training.")
        return None

    X = df[["inclination", "apogee"]]
    y = df["country"]
    
    clf = RandomForestClassifier(n_estimators=50, random_state=42)
    clf.fit(X, y)
    print(f" [ML] Classifier trained on {len(df)} verified satellites.")
    return clf

def predict_country(clf, params):
    """
    Predicts country using the trained classifier.
    """
    if clf is None:
        return "UNKNOWN", 0.0
    
    try:
        # Input must match training features: inclination, apogee
        features = pd.DataFrame([[params["inclination"], params["apogee"]]], columns=["inclination", "apogee"])
        prediction = clf.predict(features)[0]
        probs = clf.predict_proba(features)[0]
        confidence = max(probs)
        return prediction, confidence
    except Exception:
        return "ERROR", 0.0

def generate_cluster_plot(sat_dict):
    """
    Generates a scatter plot of Inclination vs Apogee, colored by Country.
    Returns base64 encoded PNG.
    """
    data = []
    for name, sat in sat_dict.items():
        params = compute_orbital_parameters(sat)
        # Re-use labeling logic for consistency in plot colors
        country = "UNKNOWN"
        upper_name = name.upper()
        if "NOAA" in upper_name or "GOES" in upper_name or "USA" in upper_name:
            country = "USA"
        elif "METEOR" in upper_name or "COSMOS" in upper_name:
            country = "RUSSIA"
        elif "FENGYUN" in upper_name:
            country = "CHINA"
        elif "METOP" in upper_name:
            country = "ESA"
            
        data.append({
            "inclination": params["inclination"],
            "apogee": params["apogee"],
            "country": country
        })
    
    df = pd.DataFrame(data)
    
    plt.figure(figsize=(10, 6))
    
    # Plot each country group
    groups = df.groupby("country")
    for name, group in groups:
        plt.scatter(group["inclination"], group["apogee"], label=name, alpha=0.6)
        
    plt.title("Orbital Fingerprint: Inclination vs Apogee")
    plt.xlabel("Inclination (deg)")
    plt.ylabel("Apogee Altitude (km)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    
    # Encode
    b64_str = base64.b64encode(buf.read()).decode('utf-8')
    
    # Also save to disk as requested
    with open("orbital_fingerprint.png", "wb") as f:
        f.write(base64.b64decode(b64_str))
    
    # Send FINGERPRINT_UPDATE event
    try:
        event = {
            "event_meta": {
                "origin_module": "space.tracker",
                "event_type": "FINGERPRINT_UPDATE",
                "severity": "INFO",
                "classification": "REAL_WORLD"
            },
            "context": {
                "related_asset_id": "ORBITAL_FINGERPRINT",
                "legal_compliance_tag": "PUBLIC_ORBITAL_DATA"
            },
            "payload": {
                "image_b64": b64_str,
                "timestamp": datetime.now(utc).isoformat()
            }
        }
        requests.post(CORE_API_URL, json=event)
        print(" [ OrbitGuard ] Sent Orbital Fingerprint Update.")
    except Exception as e:
        print(f"[!] Failed to send fingerprint update: {e}")
        
    return b64_str

# Initialize ML
print(" [ OrbitGuard ] Training ML Classifier...")
CLASSIFIER_MODEL = train_classifier(satellites, sat_metadata)
generate_cluster_plot(satellites) 

def get_next_pass(sat):
    """
    Predicts pass for a specific satellite object.
    """
    ts = load.timescale()
    t0 = ts.now()
    future_time = datetime.now(utc) + timedelta(days=1)
    t1 = ts.from_datetime(future_time)
    
    times, events = sat.find_events(GROUND_STATION, t0, t1, altitude_degrees=0.0)
    for ti, event in zip(times, events):
        if event == 0: # Rise
            return ti.utc_datetime().isoformat()
    return "NO PASS < 24H"

def telemetry_cycle():
    try:
        ts = load.timescale()
        t = ts.now()
        
        # Run Space War Detector Analysis Cycle (Once per Telemetry Cycle)
        # We pass specific inputs: All Satellite Objects, and the Metadata Map
        war_metrics = WAR_DETECTOR.run_cycle(satellites, sat_metadata)
        
        # Iterate over ALL satellites
        for name, sat in satellites.items():
            try:
                norad_id = sat.model.satnum
                
                # 0. Get/Compute Orbital Params & Prediction
                if name not in SATELLITE_DATA_CACHE:
                    params = compute_orbital_parameters(sat)
                    # Use ML Model
                    pred_country, confidence = predict_country(CLASSIFIER_MODEL, params)
                    
                    # Get Truth from Metadata
                    truth_data = sat_metadata.get(norad_id, {})
                    
                    SATELLITE_DATA_CACHE[name] = {
                        "params": params,
                        "prediction": {"country": pred_country, "confidence": round(confidence, 2)},
                        "truth": truth_data
                    }
                
                cached_data = SATELLITE_DATA_CACHE[name]
                params = cached_data["params"]
                prediction = cached_data["prediction"]
                truth = cached_data["truth"]

                # 1. Relative Position (Az/El)
                bary_sat = earth + sat
                ground_location = earth + GROUND_STATION
                topocentric = (bary_sat - ground_location).at(t)
                alt, az, distance = topocentric.altaz()

                # 2. Global Position (Lat/Lon)
                geocentric = sat.at(t)
                subpoint = wgs84.subpoint(geocentric)
                
                sat_lat = subpoint.latitude.degrees
                sat_lon = subpoint.longitude.degrees
                sat_alt = subpoint.elevation.km

                if alt.degrees > 0:
                    visibility = "VISIBLE"
                    severity = "MEDIUM" 
                else:
                    visibility = "BELOW_HORIZON"
                    severity = "INFO"

                # 3. Prediction & Path (For Priority Targets)
                next_pass_time = None
                orbit_path = []
                
                # Check priority (Exact match or substring match against our PRIORITY list or Favorite IDs)
                is_priority = False
                if any(p in name for p in PRIORITY_TARGETS): 
                    is_priority = True
                
                if is_priority:
                    # Next Pass
                    next_pass_time = get_next_pass(sat)
                    
                    # Orbit Path (90 mins) - 3D [Lat, Lon, Alt]
                    base_time = t.utc_datetime()
                    for i in range(0, 91, 2):
                        future_time = base_time + timedelta(minutes=i)
                        ts_time = ts.from_datetime(future_time)
                        sub = wgs84.subpoint(sat.at(ts_time))
                        orbit_path.append([sub.latitude.degrees, sub.longitude.degrees, sub.elevation.km])

                payload = {
                    "sat_name": name,
                    "azimuth": round(az.degrees, 2),
                    "elevation": round(alt.degrees, 2),
                    "distance_km": round(distance.km, 2),
                    "visibility": visibility,
                    "geo_lat": sat_lat,
                    "geo_lng": sat_lon,
                    "geo_alt": sat_alt,
                    "orbit_path": orbit_path, 
                    "next_pass": next_pass_time,
                    "timestamp": t.utc_iso(),
                    "tle": {
                        "line1": getattr(sat.model, 'line1', None) or getattr(sat.model, 'tle_line1', "MISSING"),
                        "line2": getattr(sat.model, 'line2', None) or getattr(sat.model, 'tle_line2', "MISSING")
                    },
                    # Enhanced Metadata
                    "orbital_params": params,
                    "origin_prediction": prediction,
                    "verified_metadata": {
                        "country": truth.get("country", "UNK"),
                        "launch_year": truth.get("launch_year", "UNK"),
                        "rcs_size": truth.get("rcs_size", "UNK"),
                        "object_name": truth.get("object_name", name)
                    },
                    # Space War Metrics (Per-Satellite Filtered)
                    "war_metrics": WAR_DETECTOR.get_per_satellite_metrics(name, war_metrics)
                }

                event = {
                    "event_meta": {
                        "origin_module": "space.tracker",
                        "event_type": "TLE_UPDATE",
                        "severity": severity,
                        "classification": "REAL_WORLD"
                    },
                    "context": {
                        "related_asset_id": f"SAT-{norad_id}",
                        "legal_compliance_tag": "PUBLIC_ORBITAL_DATA"
                    },
                    "payload": payload
                }

                requests.post(CORE_API_URL, json=event)
                
            except Exception as e_inner:
                # print(f"[!] Error processing {name}: {e_inner}")
                continue
        
        print(f"[*] Cycle complete. Telemetry sent for {len(satellites)} satellites.")

    except Exception as e:
        print(f"[!] Cycle Error: {e}")

schedule.every(5).seconds.do(telemetry_cycle)

while True:
    schedule.run_pending()
    time.sleep(1)