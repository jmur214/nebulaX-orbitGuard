class BehavioralClassifier:
    def assess(self, signals):
        """
        Aggregates individual module scores into a final escalation metric.
        """
        total_score = 0
        all_alerts = []
        
        for module, output in signals.items():
            total_score += output.get("score_contribution", 0)
            if "alerts" in output:
                all_alerts.extend(output["alerts"])
        
        # Cap Score
        total_score = min(100, total_score)
        
        # Determine DEFCON (5 is low/normal, 1 is War)
        defcon = 5
        if total_score > 80: defcon = 1
        elif total_score > 60: defcon = 2
        elif total_score > 40: defcon = 3
        elif total_score > 20: defcon = 4
        
        return {
            "total_score": total_score,
            "defcon": defcon,
            "critical_alerts": all_alerts
        }
