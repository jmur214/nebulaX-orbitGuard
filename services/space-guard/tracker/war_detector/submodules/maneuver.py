
class ManeuverDetector:
    def __init__(self):
        self.history = {} # {sat_name: {last_a: float, last_i: float}}

    def analyze(self, satellites, metadata):
        alerts = []
        score = 0
        
        for name, sat in satellites.items():
            try:
                # Basic Orbit Params
                model = sat.model
                a = model.a * 6378.137 # Semi-major axis in km
                i = model.inclo * 180.0 / 3.14159
                
                if name in self.history:
                    last_a = self.history[name]['last_a']
                    last_i = self.history[name]['last_i']
                    
                    # Deltas
                    delta_a = abs(a - last_a)
                    delta_i = abs(i - last_i)
                    
                    # Thresholds (Simulated sensitivity)
                    # Real maneuvers change SMA by km's or Inc by degrees
                    if delta_a > 5.0: # 5km change
                        alerts.append(f"MANEUVER: {name} Altitude Change (+/- {delta_a:.1f}km)")
                        score += 5
                    
                    if delta_i > 0.2: # 0.2 deg change (huge for plane change)
                        alerts.append(f"MANEUVER: {name} Plane Change ({delta_i:.2f} deg)")
                        score += 15 # Plane changes are expensive/suspicious
                
                # Update History
                self.history[name] = {'last_a': a, 'last_i': i}
                
            except: continue
            
        return {"alerts": alerts, "score_contribution": min(score, 40)}
