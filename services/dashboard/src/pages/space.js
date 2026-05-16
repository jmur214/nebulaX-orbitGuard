import React, { useState, useEffect } from 'react';
import axios from 'axios';
import dynamic from 'next/dynamic';
import { format } from 'date-fns';
import WarHeader from '../components/WarHeader';
import EventLog from '../components/EventLog';

const SatelliteGlobe = dynamic(() => import('../components/SatelliteGlobe'), {
    ssr: false,
    loading: () => <div className="h-[350px] w-full bg-slate-900 animate-pulse text-emerald-800 flex items-center justify-center">INITIALIZING ORBITAL ENGINE...</div>
});

export default function SpaceCommand() {
    const [events, setEvents] = useState([]);
    const [satellites, setSatellites] = useState({}); // Map of sat_name -> data
    const [fingerprint, setFingerprint] = useState(null);
    const [selectedSatName, setSelectedSatName] = useState(null); // NULL = Monitor Mode (View All)
    const [filterCountry, setFilterCountry] = useState("ALL");
    const [orbitPath, setOrbitPath] = useState(null); // On-demand orbit path
    const [orbitError, setOrbitError] = useState(null); // Per-satellite orbit fetch failure

    // ERROR DISPLAY
    const [lastError, setLastError] = useState(null);

    // Derived state
    const satList = Object.values(satellites);

    // 1. Get Unique Countries for Dropdown
    const countries = ["ALL", ...new Set(satList.map(s => s.origin_prediction?.country || "UNKNOWN"))].sort();

    // 2. Filter Satellites
    const filteredSatellites = satList.filter(s => {
        if (filterCountry === "ALL") return true;
        return (s.origin_prediction?.country || "UNKNOWN") === filterCountry;
    });

    // 3. Get Selected Object (if any)
    const selectedSat = satellites[selectedSatName] || null;

    useEffect(() => {
        const fetchData = async () => {
            try {
                const API_HOST = process.env.NEXT_PUBLIC_API_HOST || 'http://localhost:8000';
                const response = await axios.get(`${API_HOST}/events/recent?limit=200&team=space`);
                setEvents(response.data);

                const newSatellites = {};
                let latestFingerprint = null;

                for (const event of response.data) {
                    if (event.origin_module === 'space.tracker') {
                        if (event.event_type === 'TLE_UPDATE') {
                            const payload = event.payload;
                            if (!newSatellites[payload.sat_name]) {
                                newSatellites[payload.sat_name] = payload;
                            }
                        } else if (event.event_type === 'FINGERPRINT_UPDATE') {
                            if (!latestFingerprint) latestFingerprint = event.payload.image_b64;
                        }
                    }
                }

                // Replace (don't merge) so satellites the tracker stops emitting drop out.
                // Merging caused stale "ghost" satellites whose orbit fetch would 404.
                setSatellites(newSatellites);
                if (latestFingerprint) setFingerprint(latestFingerprint);
                setLastError(null);

            } catch (error) {
                console.error("Connection Error:", error);
                setLastError(error.message);
                // On error, leave satellites as-is; the red error banner surfaces the failure.
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, []);

    // Helper for Countdown
    const getCountdown = (nextPass, visibility) => {
        if (visibility === 'VISIBLE') return "TARGET ACTIVE";
        if (!nextPass || nextPass === "NO PASS < 24H") return "NO PASS < 24H";

        const diff = new Date(nextPass) - new Date();
        if (diff <= 0) return "ACQUIRING..."; // Should be handled by visibility check mostly, but fallback

        const hours = Math.floor(diff / 3600000);
        const minutes = Math.floor((diff % 3600000) / 60000);
        const seconds = Math.floor((diff % 60000) / 1000);
        return `T-MINUS ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    };

    // Handle satellite selection - fetch orbit on-demand
    const handleSatelliteSelect = async (sat) => {
        if (!sat) {
            setSelectedSatName(null);
            setOrbitPath(null);
            setOrbitError(null);
            return;
        }

        setSelectedSatName(sat.sat_name);
        setOrbitPath(null); // Clear previous
        setOrbitError(null);

        // Skip orbit fetch if TLE is known-missing (the API would 404 anyway).
        const tleLine1 = sat.tle?.line1;
        if (!tleLine1 || tleLine1 === "MISSING") {
            setOrbitError("No TLE data on file for this satellite");
            return;
        }

        // Fetch orbit path on-demand
        try {
            const API_HOST = process.env.NEXT_PUBLIC_API_HOST || 'http://localhost:8000';
            const response = await axios.get(`${API_HOST}/satellite/orbit?sat_name=${encodeURIComponent(sat.sat_name)}`);
            setOrbitPath(response.data.orbit_path);
            console.log(`Fetched orbit for ${sat.sat_name}: ${response.data.points} points`);
        } catch (error) {
            if (error.response?.status === 404) {
                setOrbitError("No recent TLE for this satellite");
            } else {
                setOrbitError(`Orbit fetch failed: ${error.message}`);
            }
            setOrbitPath(null);
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 text-emerald-400 font-mono p-6 selection:bg-emerald-900 selection:text-white">
            <WarHeader title="ORBITGUARD" subtitle="SPACE COMMAND" />

            {/* TELEMETRY LINK ERROR BANNER */}
            {lastError && (
                <div className="bg-red-900/80 text-white p-4 mb-4 border border-red-500 font-bold animate-pulse text-center">
                    ⚠ TELEMETRY LINK FAILURE ({lastError}) — RETRYING
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* LEFT COL: MAP & TELEMETRY */}
                <div className="lg:col-span-6 space-y-6">
                    <div className="shadow-[0_0_20px_rgba(16,185,129,0.2)] border border-emerald-900/30 relative h-[600px] bg-slate-900 overflow-hidden rounded-lg">
                        <SatelliteGlobe
                            satellites={filteredSatellites}
                            selectedSat={selectedSat}
                            orbitPath={orbitPath}
                            fingerprint={fingerprint}
                            onSatelliteSelect={handleSatelliteSelect}
                        />

                        {/* CONTROLS OVERLAY */}
                        <div className="absolute top-2 left-2 z-[400] flex flex-col gap-2">
                            {/* Country Filter */}
                            <select
                                value={filterCountry}
                                onChange={(e) => {
                                    setFilterCountry(e.target.value);
                                    setSelectedSatName(null); // Reset selection on filter change
                                }}
                                className="bg-slate-900/90 border border-emerald-500 text-emerald-400 text-xs p-1 rounded shadow-lg outline-none uppercase font-bold"
                            >
                                {countries.map(c => <option key={c} value={c}>FILTER: {c}</option>)}
                            </select>

                            {/* Satellite Selector */}
                            <select
                                value={selectedSatName || ""}
                                onChange={(e) => setSelectedSatName(e.target.value || null)}
                                className="bg-slate-900/90 border border-emerald-500 text-emerald-400 text-xs p-1 rounded shadow-lg outline-none"
                            >
                                <option value="">-- MONITOR MODE (VIEW ALL) --</option>
                                {filteredSatellites.sort((a, b) => a.sat_name.localeCompare(b.sat_name)).map(s => (
                                    <option key={s.sat_name} value={s.sat_name}>{s.sat_name}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {selectedSat ? (
                        <div className="bg-slate-900/50 p-6 border border-emerald-900/30 shadow-lg">
                            <div className="flex justify-between items-end mb-4 border-b border-emerald-900/30 pb-2">
                                <div>
                                    <h2 className="text-xl font-black text-white">{selectedSat.sat_name}</h2>
                                    <div className="flex gap-4 text-xs mt-1">
                                        <div className="text-slate-500">
                                            ID: <span className="text-emerald-400 font-mono">NORAD-{selectedSat.context?.related_asset_id.replace('SAT-', '') || "UNK"}</span>
                                        </div>
                                        <div className="text-slate-500">
                                            LAUNCH: <span className="text-white">{selectedSat.verified_metadata?.launch_year || "UNK"}</span>
                                        </div>
                                        <div className="text-slate-500">
                                            RCS: <span className="text-white">{selectedSat.verified_metadata?.rcs_size || "UNK"}</span>
                                        </div>
                                    </div>

                                    {/* AI VALIDATION BLOCK */}
                                    <div className="mt-2 bg-slate-950 p-2 border border-emerald-900/30 flex items-center gap-3">
                                        <div className="text-[10px] text-cyan-500 font-bold">
                                            AI PREDICTION: {selectedSat.origin_prediction?.country} ({Math.round(selectedSat.origin_prediction?.confidence * 100)}%)
                                        </div>
                                        <div className="text-[10px] text-emerald-500 font-bold border-l border-slate-700 pl-3">
                                            ✔ VERIFIED: {selectedSat.verified_metadata?.country || "UNK"}
                                        </div>
                                    </div>

                                    {/* ORBIT PATH STATUS */}
                                    <div className="mt-2 text-[10px] font-bold">
                                        {orbitError ? (
                                            <span className="text-amber-500">⚠ ORBIT: {orbitError}</span>
                                        ) : orbitPath ? (
                                            <span className="text-cyan-400">◉ ORBIT PATH LOADED ({orbitPath.length} points)</span>
                                        ) : (
                                            <span className="text-slate-500">◌ ORBIT: computing…</span>
                                        )}
                                    </div>

                                </div>
                                <div className={`text-xl font-bold ${selectedSat.visibility === 'VISIBLE' ? 'text-red-500 animate-pulse' : 'text-emerald-500'}`}>
                                    {selectedSat.visibility === 'VISIBLE' ? "/// LOS ESTABLISHED" : "/// ACQUIRING"}
                                </div>
                            </div>

                            {/* COUNTDOWN */}
                            <div className="mb-6 bg-slate-950 p-4 text-center border border-emerald-900/50">
                                <div className="text-xs text-slate-500 tracking-[0.2em] mb-1">NEXT PASS (UTC)</div>
                                <div className="text-4xl font-black text-white tracking-tighter">
                                    {getCountdown(selectedSat.next_pass, selectedSat.visibility)}
                                </div>
                            </div>

                            <div className="grid grid-cols-3 gap-4 text-center">
                                <div className="bg-slate-950 p-4 border border-emerald-900/30">
                                    <div className="text-xs text-slate-500">AZIMUTH</div>
                                    <div className="text-2xl text-white font-bold">{selectedSat.azimuth}°</div>
                                </div>
                                <div className="bg-slate-950 p-4 border border-emerald-900/30">
                                    <div className="text-xs text-slate-500">ELEVATION</div>
                                    <div className="text-2xl text-white font-bold">{selectedSat.elevation}°</div>
                                </div>
                                <div className="bg-slate-950 p-4 border border-emerald-900/30">
                                    <div className="text-xs text-slate-500">RANGE</div>
                                    <div className="text-2xl text-white font-bold">{selectedSat.distance_km} km</div>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="bg-slate-900/30 p-10 border border-emerald-900/20 text-center">
                            <div className="text-emerald-500/50 font-black text-2xl mb-2">GLOBAL MONITORING ACTIVE</div>
                            <div className="text-slate-500 text-sm">TRACKING {filteredSatellites.length} OBJECTS IN SECTOR</div>
                            <div className="mt-4 text-xs text-slate-600 animate-pulse">AWAITING TARGET DESIGNATION...</div>
                        </div>
                    )}
                </div>

                {/* RIGHT COL: STRATEGIC ANALYSIS & EVENT LOG */}
                <div className="lg:col-span-6 space-y-6">
                    {/* SPACE WAR DETECTOR PANEL */}
                    <div className="bg-slate-950 border border-red-900/50 p-6 relative overflow-hidden">
                        {/* Background warning stripes if DEFCON < 3 */}
                        {selectedSat?.war_metrics?.defcon_level <= 3 && (
                            <div className="absolute inset-0 bg-[repeating-linear-gradient(45deg,transparent,transparent_10px,rgba(220,38,38,0.1)_10px,rgba(220,38,38,0.1)_20px)] pointer-events-none" />
                        )}

                        <div className="flex justify-between items-start relative z-10">
                            <div>
                                <h3 className="text-red-500 font-black tracking-widest text-lg mb-1">STRATEGIC ANALYSIS</h3>
                                <div className="text-xs text-red-400/70">BEHAVIORAL ESCALATION MONITOR</div>
                            </div>
                            <div className="text-right">
                                <div className="text-xs text-slate-500 mb-1">DEFCON LEVEL</div>
                                <div className={`text-5xl font-black ${(selectedSat?.war_metrics?.defcon_level || 5) <= 2 ? 'text-red-500 animate-pulse' :
                                    (selectedSat?.war_metrics?.defcon_level || 5) <= 3 ? 'text-orange-500' : 'text-emerald-500'
                                    }`}>
                                    {selectedSat?.war_metrics?.defcon_level || 5}
                                </div>
                            </div>
                        </div>

                        {/* ESCALATION SCORE */}
                        <div className="mt-6 relative z-10">
                            <div className="flex justify-between text-xs mb-1">
                                <span className={
                                    (selectedSat?.war_metrics?.escalation_score || 0) > 75 ? "text-red-400 font-bold" : "text-slate-400"
                                }>RISK SCORE</span>
                                <span className="text-white font-mono">{selectedSat?.war_metrics?.escalation_score || 0}/100</span>
                            </div>
                            <div className="h-2 bg-slate-900 w-full overflow-hidden">
                                <div
                                    className={`h-full transition-all duration-1000 ${(selectedSat?.war_metrics?.escalation_score || 0) > 75 ? 'bg-red-600' :
                                        (selectedSat?.war_metrics?.escalation_score || 0) > 40 ? 'bg-orange-500' : 'bg-emerald-600'
                                        }`}
                                    style={{ width: `${selectedSat?.war_metrics?.escalation_score || 0}%` }}
                                />
                            </div>
                        </div>

                        {/* ACTIVE ALERTS */}
                        <div className="mt-6 relative z-10">
                            <div className="text-xs text-slate-500 mb-2 border-b border-slate-800 pb-1">ACTIVE SIGNALS</div>
                            <div className="space-y-2 h-[120px] overflow-y-auto pr-2">
                                {selectedSat?.war_metrics?.active_alerts?.length > 0 ? (
                                    selectedSat.war_metrics.active_alerts.map((alert, i) => (
                                        <div key={i} className="text-xs bg-red-950/30 border-l-2 border-red-600 p-2 text-red-200 font-mono">
                                            {alert}
                                        </div>
                                    ))
                                ) : (
                                    <div className="text-xs text-emerald-600 italic p-2">NO ANOMALOUS BEHAVIOR DETECTED</div>
                                )}
                            </div>
                        </div>
                    </div>

                    <div className="h-[400px]">
                        <EventLog events={events} title="ORBITAL TELEMETRY" />
                    </div>
                </div>
            </div>
        </div>
    );
}
