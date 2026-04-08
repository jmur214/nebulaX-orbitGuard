"""
Orbit Computer Module
Computes satellite orbit paths on-demand using TLE data and Skyfield.
"""
from skyfield.api import EarthSatellite, load, wgs84
from datetime import datetime, timedelta, timezone
from typing import List, Tuple, Optional
import io

# Load timescale once
ts = load.timescale()


def compute_orbit_path(tle_line1: str, tle_line2: str, sat_name: str = "SAT", 
                       duration_minutes: int = 90, interval_minutes: int = 2,
                       start_time: Optional[datetime] = None) -> List[List[float]]:
    """
    Computes orbit path from TLE data.
    
    Args:
        tle_line1: TLE line 1
        tle_line2: TLE line 2
        sat_name: Satellite name (optional)
        duration_minutes: How far into the future to predict (default 90 min)
        interval_minutes: Time between points (default 2 min)
        start_time: When to start the orbit from (default: now)
    
    Returns:
        List of [latitude, longitude, altitude_km] points
    """
    try:
        # Create satellite from TLE
        satellite = EarthSatellite(tle_line1, tle_line2, sat_name, ts)
        
        # Use provided start time or current time
        if start_time is None:
            start_time = datetime.now(timezone.utc)
        elif start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
            
        orbit_path = []
        
        # Compute positions at regular intervals
        for minutes in range(0, duration_minutes + 1, interval_minutes):
            future_time = start_time + timedelta(minutes=minutes)
            t = ts.from_datetime(future_time)
            
            # Get subpoint (lat, lon, alt)
            geocentric = satellite.at(t)
            subpoint = wgs84.subpoint(geocentric)
            
            lat = subpoint.latitude.degrees
            lon = subpoint.longitude.degrees
            alt = subpoint.elevation.km
            
            orbit_path.append([lat, lon, alt])
        
        return orbit_path
    
    except Exception as e:
        print(f"[!] Orbit computation error: {e}")
        return []


def get_current_position(tle_line1: str, tle_line2: str, sat_name: str = "SAT") -> Optional[dict]:
    """
    Gets current position of satellite.
    
    Returns:
        Dict with lat, lon, alt_km or None on error
    """
    try:
        satellite = EarthSatellite(tle_line1, tle_line2, sat_name, ts)
        t = ts.now()
        
        geocentric = satellite.at(t)
        subpoint = wgs84.subpoint(geocentric)
        
        return {
            "lat": subpoint.latitude.degrees,
            "lon": subpoint.longitude.degrees,
            "alt_km": subpoint.elevation.km
        }
    except Exception as e:
        print(f"[!] Position computation error: {e}")
        return None
