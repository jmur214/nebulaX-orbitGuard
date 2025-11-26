import time
import json
import requests
import schedule
# --- UPDATED IMPORT: Added 'utc' ---
from skyfield.api import Topos, load, wgs84, utc
from datetime import datetime, timedelta

# CONFIGURATION
CORE_API_URL = "http://host.docker.internal:8000/events/ingest"
# Chicago Coordinates
GROUND_STATION = Topos('41.8952 N', '87.8257 W')

print(" [ OrbitGuard ] Satellite Tracking System Online...")

# 1. Load Data
eph = load('de421.bsp')
earth = eph['earth']

print(" [ OrbitGuard ] Downloading TLE data...")
satellites_list = load.tle_file(url='https://celestrak.org/NORAD/elements/weather.txt', reload=False)
satellites = {sat.name: sat for sat in satellites_list}

desired_target = "NOAA 20 (JPSS-1)"
final_target_name = None

if desired_target in satellites:
    final_target_name = desired_target
else:
    for name in satellites.keys():
        if "NOAA 20" in name:
            final_target_name = name
            break

if not final_target_name:
    print(f"[!] Critical: Target not found.")
    exit(1)

# Separate objects for map vs calculations
raw_satellite = satellites[final_target_name]
barycentric_satellite = earth + raw_satellite

print(f" [ OrbitGuard ] Acquired Target: {final_target_name}")

def get_next_pass():
    """
    Predicts the next time the satellite will rise above the horizon.
    """
    ts = load.timescale()
    t0 = ts.now()
    
    # --- FIX IS HERE ---
    # We must use datetime.now(utc) instead of utcnow() to ensure the object is timezone-aware
    future_time = datetime.now(utc) + timedelta(days=1)
    t1 = ts.from_datetime(future_time)
    
    # Find events: 0=Rise, 1=Culminate (Peak), 2=Set
    times, events = raw_satellite.find_events(GROUND_STATION, t0, t1, altitude_degrees=0.0)
    
    for ti, event in zip(times, events):
        if event == 0: # Rise event
            return ti.utc_datetime().isoformat()
            
    return "NO PASS < 24H"

def telemetry_cycle():
    try:
        ts = load.timescale()
        t = ts.now()

        # 1. Relative Position (Az/El)
        ground_location = earth + GROUND_STATION
        topocentric = (barycentric_satellite - ground_location).at(t)
        alt, az, distance = topocentric.altaz()

        # 2. Global Position (Lat/Lon)
        geocentric = raw_satellite.at(t)
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

        # 3. Prediction
        next_pass_time = get_next_pass()

        # 4. Orbit Path Calculation (Next 90 minutes)
        orbit_path = []
        base_time = t.utc_datetime()
        
        for i in range(0, 91, 2):
            future_time = base_time + timedelta(minutes=i)
            ts_time = ts.from_datetime(future_time)
            geo = raw_satellite.at(ts_time)
            sub = wgs84.subpoint(geo)
            orbit_path.append([sub.latitude.degrees, sub.longitude.degrees])

        payload = {
            "sat_name": final_target_name,
            "azimuth": round(az.degrees, 2),
            "elevation": round(alt.degrees, 2),
            "distance_km": round(distance.km, 2),
            "visibility": visibility,
            "geo_lat": sat_lat,
            "geo_lng": sat_lon,
            "geo_alt": sat_alt,
            "orbit_path": orbit_path, # New Field
            "next_pass": next_pass_time,
            "timestamp": t.utc_iso()
        }

        event = {
            "event_meta": {
                "origin_module": "space.tracker",
                "event_type": "TLE_UPDATE",
                "severity": severity,
                "classification": "REAL_WORLD"
            },
            "context": {
                "related_asset_id": f"SAT-{final_target_name}",
                "legal_compliance_tag": "PUBLIC_ORBITAL_DATA"
            },
            "payload": payload
        }

        requests.post(CORE_API_URL, json=event)
        
        print(f"[*] Vis: {visibility} | Next Pass: {next_pass_time}")

    except Exception as e:
        print(f"[!] Cycle Error: {e}")

schedule.every(5).seconds.do(telemetry_cycle)

while True:
    schedule.run_pending()
    time.sleep(1)