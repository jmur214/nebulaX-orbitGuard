from skyfield.api import load
import logging

# ISS Components - These are all docked/attached to the ISS
# and should not be compared against each other
ISS_COMPONENTS = {
    "ISS", "ZARYA", "NAUKA", "UNITY", "DESTINY", "COLUMBUS", "KIBO",
    "PROGRESS", "SOYUZ", "DRAGON", "CYGNUS", "HTV", "CREW DRAGON",
    "STARLINER", "ZVEZDA", "RASSVET", "PIRS", "POISK"
}

def is_iss_component(name):
    """Check if a satellite name is part of the ISS complex."""
    name_upper = name.upper()
    return any(comp in name_upper for comp in ISS_COMPONENTS)

def is_same_platform(name1, name2):
    """Check if both names are ISS components (shouldn't alert on each other)."""
    return is_iss_component(name1) and is_iss_component(name2)

class ProximityDetector:
    def __init__(self):
        self.ts = load.timescale()
        self.logger = logging.getLogger("ProximityDetector")
        
    def analyze(self, satellites, metadata):
        alerts = []
        score = 0
        per_sat_alerts = {}  # {sat_name: [alerts]} for per-satellite filtering
        
        t = self.ts.now()
        
        # Filter for active/interesting sats to check against
        # Check things approaching ISS, NOAA weather sats, or US military assets
        targets = []
        for n, s in satellites.items():
            if "ISS" in n or "NOAA" in n or "USA" in n or "NAVSTAR" in n:
                targets.append((n, s))
        
        others = [(n, s) for n, s in satellites.items()]
        
        for t_name, target in targets:
            try:
                t_pos = target.at(t).position.km
                
                for o_name, other in others:
                    if t_name == o_name: 
                        continue
                    
                    # Skip ISS self-comparisons (docked modules)
                    if is_same_platform(t_name, o_name):
                        continue
                    
                    try:
                        o_pos = other.at(t).position.km
                        
                        # Euclidean Distance
                        dist = ((t_pos[0]-o_pos[0])**2 + (t_pos[1]-o_pos[1])**2 + (t_pos[2]-o_pos[2])**2)**0.5
                        
                        if dist < 50.0:  # 50km Proximity Warning
                            alert = f"PROXIMITY: {o_name} < {dist:.1f}km from {t_name}"
                            alerts.append(alert)
                            score += 10
                            
                            # Track per-satellite involvement
                            if t_name not in per_sat_alerts:
                                per_sat_alerts[t_name] = []
                            if o_name not in per_sat_alerts:
                                per_sat_alerts[o_name] = []
                            per_sat_alerts[t_name].append(alert)
                            per_sat_alerts[o_name].append(alert)
                            
                            if dist < 10.0:  # Close intercept
                                score += 20
                                
                    except Exception as e:
                        continue
                        
            except Exception as e:
                continue
             
        return {
            "alerts": list(set(alerts)), 
            "score_contribution": min(score, 50),
            "per_satellite": per_sat_alerts
        }
