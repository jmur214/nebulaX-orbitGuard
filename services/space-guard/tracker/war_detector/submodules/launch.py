import requests
import logging
from datetime import datetime, timedelta, timezone
import time

# Sites of strategic interest for "unscheduled" or adversary launch monitoring
ADVERSARY_SITES = {
    "Plesetsk",      # Russia - Military launches
    "Jiuquan",       # China - Military/Dual-use
    "Baikonur",      # Kazakhstan (Russian operated)
    "Xichang",       # China - GEO launches
    "Taiyuan",       # China - Polar launches
    "Sriharikota",   # India - ISRO
    "Vostochny",     # Russia - New spaceport
}

class LaunchMonitor:
    def __init__(self):
        self.logger = logging.getLogger("LaunchMonitor")
        self.cache = None
        self.cache_time = None
        self.cache_duration = 300  # 5 minutes (to respect 15 req/hour limit)
        self.api_url = "https://ll.thespacedevs.com/2.2.0/launch/upcoming/?limit=5"
        
    def _fetch_launches(self):
        """Fetch upcoming launches from Launch Library 2 API."""
        # Check cache first
        if self.cache and self.cache_time:
            if time.time() - self.cache_time < self.cache_duration:
                return self.cache
        
        try:
            response = requests.get(self.api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.cache = data.get('results', [])
                self.cache_time = time.time()
                self.logger.info(f" [Launch] Fetched {len(self.cache)} upcoming launches")
                return self.cache
            else:
                self.logger.warning(f" [Launch] API returned {response.status_code}")
                return self.cache or []
        except Exception as e:
            self.logger.warning(f" [Launch] API Error: {e}")
            return self.cache or []
    
    def analyze(self, satellites, metadata):
        alerts = []
        score = 0
        
        try:
            launches = self._fetch_launches()
            now = datetime.now(timezone.utc)
            
            for launch in launches:
                try:
                    # Parse launch time
                    net = launch.get('net')  # NET = No Earlier Than
                    if not net:
                        continue
                    
                    # Handle ISO format with timezone
                    launch_time = datetime.fromisoformat(net.replace('Z', '+00:00'))
                    time_diff = launch_time - now
                    
                    # Get launch site info
                    pad = launch.get('pad', {})
                    location = pad.get('location', {})
                    site_name = location.get('name', 'Unknown')
                    country = location.get('country_code', 'UNK')
                    
                    rocket = launch.get('rocket', {})
                    rocket_name = rocket.get('configuration', {}).get('name', 'Unknown Rocket')
                    mission_name = launch.get('mission', {})
                    mission_name = mission_name.get('name', 'Unknown Mission') if mission_name else 'Unknown Mission'
                    
                    # Check if this is from a site of interest
                    is_adversary = any(site in site_name for site in ADVERSARY_SITES)
                    
                    # Alert for imminent launches (< 6 hours)
                    if timedelta(hours=0) <= time_diff <= timedelta(hours=6):
                        hours_until = time_diff.total_seconds() / 3600
                        
                        if is_adversary:
                            alerts.append(f"LAUNCH: {rocket_name} from {site_name} in {hours_until:.1f}h - {mission_name}")
                            score += 15  # Higher score for adversary sites
                        else:
                            # Still track friendly launches but lower score
                            alerts.append(f"LAUNCH: {rocket_name} from {site_name} in {hours_until:.1f}h")
                            score += 5
                    
                    # High priority alert for very imminent launches (< 1 hour)
                    if timedelta(hours=0) <= time_diff <= timedelta(hours=1):
                        if is_adversary:
                            score += 10  # Additional score for imminent adversary launch
                            
                except Exception:
                    continue
                    
        except Exception as e:
            self.logger.error(f" [Launch] Analysis error: {e}")
            
        return {"alerts": alerts, "score_contribution": min(score, 30)}
