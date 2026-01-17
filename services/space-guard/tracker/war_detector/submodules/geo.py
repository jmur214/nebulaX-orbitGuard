class GEOSentinel:
    def analyze(self, satellites, metadata):
        alerts = []
        score = 0
        
        for name, sat in satellites.items():
            try:
                model = sat.model
                # Check if GEO (Mean Motion approx 1.0 rev/day)
                # mm is revs per day in SGP4 (usually), but skyfield 'no_kozai' is rad/min
                # Let's use Period: approx 1436 minutes
                
                a = model.a * 6378.137
                period = 2 * 3.14159 * a**1.5 / 398600.4418**0.5 / 60
                
                if 1430 < period < 1440: # GEO Belt
                    # Check Inclination (Stationkeeping)
                    inc = model.inclo * 180.0 / 3.14159
                    
                    if inc > 5.0: # High inclination GEO (Old or Special Purpose)
                        # Not necessarily hostile, but interesting
                        pass
                        
                    # Real "War" metric: Is it drifting aggressively near other slots?
                    # This requires tracking longitude over time. 
                    # For now, we simulate a "Drift Alert" for specific demo satellites
                    if "LUCH" in name or "OLYMP" in name: # Known Russian Inspector sats
                        alerts.append(f"GEO SENTINEL: Inspector {name} Active in Belt")
                        score += 10

            except: continue
            
        return {"alerts": alerts, "score_contribution": score}
