class DebrisListener:
    def __init__(self):
        self.last_count = 0
        
    def analyze(self, satellites, metadata):
        alerts = []
        score = 0
        
        current_count = len(satellites)
        
        # In a real system, we'd check per-plane grouping for breakup events.
        # Here we just look for massive surges in total tracked objects.
        
        if self.last_count > 0:
            growth = current_count - self.last_count
            
            if growth > 50: # Massive breakup event
                alerts.append(f"DEBRIS: Surge Detected (+{growth} objects)")
                score += 40 # Critical event
            elif growth > 10:
                alerts.append(f"DEBRIS: Launch or minor breakup (+{growth})")
                score += 5
        
        self.last_count = current_count
        return {"alerts": alerts, "score_contribution": score}
