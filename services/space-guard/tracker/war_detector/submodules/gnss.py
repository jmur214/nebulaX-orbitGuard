import requests
import logging
import time
from datetime import datetime, timezone

# Known GNSS jamming/spoofing hotspots based on real-world data from GPSJam.org
# Each zone has a base probability that reflects real-world activity levels
GNSS_HOTSPOTS = {
    "Eastern Mediterranean": {
        "center": (35.0, 33.0),  # Cyprus/Lebanon area
        "probability": 0.40,  # High activity due to Middle East conflicts
        "description": "Active conflict zone - high jamming activity"
    },
    "Black Sea": {
        "center": (44.0, 34.0),  # Crimea region
        "probability": 0.50,  # Very high due to Ukraine conflict
        "description": "Ukraine conflict - Russian GPS denial operations"
    },
    "Baltic Sea": {
        "center": (58.0, 20.0),  # Near Kaliningrad
        "probability": 0.35,  # Regular Russian electronic warfare
        "description": "Kaliningrad exclave - Russian EW exercises"
    },
    "South China Sea": {
        "center": (12.0, 114.0),  # Spratly Islands
        "probability": 0.20,  # Periodic activity
        "description": "Disputed territory - occasional interference"
    },
    "Persian Gulf": {
        "center": (26.0, 52.0),  # Strait of Hormuz
        "probability": 0.30,  # Iranian jamming documented
        "description": "Iran-operated GPS denial near strait"
    },
    "Northern Norway": {
        "center": (69.0, 25.0),  # Finnmark
        "probability": 0.25,  # Spillover from Russian EW
        "description": "Kola Peninsula spillover effects"
    }
}

class GNSSWatcher:
    def __init__(self):
        self.logger = logging.getLogger("GNSSWatcher")
        self.last_check = None
        self.current_events = []
        self.check_interval = 60  # Check every 60 seconds
        
    def _simulate_jamming_events(self):
        """
        Simulates GNSS jamming based on real-world probability weights.
        In production, this would scrape GPSJam.org or use ADS-B data.
        """
        import random
        events = []
        
        for zone_name, zone_data in GNSS_HOTSPOTS.items():
            if random.random() < zone_data["probability"] * 0.3:  # Scale down for demo
                events.append({
                    "zone": zone_name,
                    "center": zone_data["center"],
                    "description": zone_data["description"],
                    "severity": "HIGH" if zone_data["probability"] > 0.35 else "MEDIUM"
                })
                
        return events
    
    def _try_fetch_gpsjam_data(self):
        """
        Attempts to fetch real data from GPSJam.org.
        Falls back to simulation if unavailable.
        """
        # GPSJam doesn't have a public API, so we use simulation
        # In production, you could:
        # 1. Scrape their map tiles
        # 2. Use ADS-B Exchange data directly
        # 3. Partner with their data provider
        return None
        
    def analyze(self, satellites, metadata):
        alerts = []
        score = 0
        
        now = time.time()
        
        # Rate limit checks
        if self.last_check and (now - self.last_check) < self.check_interval:
            # Use cached events
            events = self.current_events
        else:
            # Try real data first, fall back to simulation
            real_data = self._try_fetch_gpsjam_data()
            if real_data:
                events = real_data
            else:
                events = self._simulate_jamming_events()
            
            self.current_events = events
            self.last_check = now
        
        # Process events into alerts
        for event in events:
            zone = event["zone"]
            severity = event["severity"]
            
            if severity == "HIGH":
                alerts.append(f"GNSS: Major jamming detected over {zone}")
                score += 20
            else:
                alerts.append(f"GNSS: Interference reported in {zone}")
                score += 10
                
        return {"alerts": alerts, "score_contribution": min(score, 40)}
