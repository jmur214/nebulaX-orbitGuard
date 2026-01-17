import logging
import time
from .submodules.maneuver import ManeuverDetector
from .submodules.proximity import ProximityDetector
from .submodules.debris import DebrisListener
from .submodules.gnss import GNSSWatcher
from .submodules.launch import LaunchMonitor
from .submodules.geo import GEOSentinel
from .scoring.classifier import BehavioralClassifier

class SpaceWarDetector:
    def __init__(self):
        self.logger = logging.getLogger("SpaceWarDetector")
        
        # Initialize Submodules
        self.modules = {
            "maneuver": ManeuverDetector(),
            "proximity": ProximityDetector(),
            "debris": DebrisListener(),
            "gnss": GNSSWatcher(),
            "launch": LaunchMonitor(),
            "geo": GEOSentinel()
        }
        
        self.classifier = BehavioralClassifier()
        self.history = []
        self._last_global_metrics = None
        self._per_sat_proximity = {}

    def run_cycle(self, satellites, metadata):
        """
        Runs one full detection cycle across all 6 modules.
        Args:
            satellites (dict): Dict of Skyfield satellite objects.
            metadata (dict): Metadata map (Ground Truth).
        """
        self.logger.info(" [WarDetector] Starting Analysis Cycle...")
        start_time = time.time()
        
        raw_signals = {}
        
        # 1. Run all Generators
        for name, module in self.modules.items():
            try:
                raw_signals[name] = module.analyze(satellites, metadata)
            except Exception as e:
                self.logger.error(f"Module '{name}' failed: {e}")
                raw_signals[name] = {"alerts": [], "score_contribution": 0}
        
        # Store per-satellite proximity data if available
        if "per_satellite" in raw_signals.get("proximity", {}):
            self._per_sat_proximity = raw_signals["proximity"]["per_satellite"]

        # 2. Fuse & Classify
        final_assessment = self.classifier.assess(raw_signals)
        
        self.logger.info(f" [WarDetector] Cycle complete in {time.time() - start_time:.2f}s. Score: {final_assessment['total_score']}")
        
        self._last_global_metrics = {
            "escalation_score": final_assessment['total_score'],
            "defcon_level": final_assessment['defcon'],
            "module_outputs": raw_signals,
            "active_alerts": final_assessment['critical_alerts']
        }
        
        return self._last_global_metrics
    
    def get_per_satellite_metrics(self, sat_name, global_metrics=None):
        """
        Filter global alerts to those relevant to a specific satellite.
        This allows each satellite to show only alerts it's involved in.
        
        Args:
            sat_name (str): Name of the satellite
            global_metrics (dict): Optional global metrics, uses cached if not provided
            
        Returns:
            dict: Filtered metrics for this satellite
        """
        if global_metrics is None:
            global_metrics = self._last_global_metrics or {}
            
        if not global_metrics:
            return {
                "escalation_score": 0,
                "defcon_level": 5,
                "active_alerts": [],
                "relevant_alerts": [],
                "is_involved": False,
                "module_outputs": {}
            }
        
        # Filter alerts that mention this satellite
        all_alerts = global_metrics.get("active_alerts", [])
        relevant_alerts = [a for a in all_alerts if sat_name in a]
        
        # Also check per-satellite proximity data
        proximity_alerts = self._per_sat_proximity.get(sat_name, [])
        for pa in proximity_alerts:
            if pa not in relevant_alerts:
                relevant_alerts.append(pa)
        
        # Calculate satellite-specific score contribution
        sat_score = 0
        if relevant_alerts:
            # 10 points per proximity alert this sat is involved in
            sat_score = len(relevant_alerts) * 10
        
        # Add global threats (GNSS, Launch) that affect everyone
        module_outputs = global_metrics.get("module_outputs", {})
        gnss_alerts = module_outputs.get("gnss", {}).get("alerts", [])
        launch_alerts = module_outputs.get("launch", {}).get("alerts", [])
        
        # These are global threats - add them but don't duplicate
        global_threats = gnss_alerts + launch_alerts
        for gt in global_threats:
            if gt not in relevant_alerts:
                relevant_alerts.append(gt)
                sat_score += 5  # Lower weight for global threats
        
        # Determine satellite-specific DEFCON
        sat_defcon = 5
        if sat_score > 40: sat_defcon = 2
        elif sat_score > 20: sat_defcon = 3
        elif sat_score > 10: sat_defcon = 4
        elif sat_score > 0: sat_defcon = 4
        
        return {
            "escalation_score": min(sat_score, 100),
            "defcon_level": sat_defcon,
            "active_alerts": relevant_alerts,
            "is_involved": len(relevant_alerts) > 0,
            "global_defcon": global_metrics.get("defcon_level", 5),
            "global_score": global_metrics.get("escalation_score", 0),
            "module_outputs": module_outputs
        }
