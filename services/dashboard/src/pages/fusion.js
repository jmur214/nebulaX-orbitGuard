import React, { useState, useEffect } from 'react';
import axios from 'axios';
import dynamic from 'next/dynamic';
import WarHeader from '../components/WarHeader';
import EventLog from '../components/EventLog';
import AttackChart from '../components/AttackChart';
import NetworkTrafficChart from '../components/NetworkTrafficChart';

const SatelliteMap = dynamic(() => import('../components/SatelliteMap'), {
    ssr: false,
    loading: () => <div className="h-[200px] w-full bg-slate-900 animate-pulse">LOADING...</div>
});

export default function FusionCenter() {
    const [events, setEvents] = useState([]);
    const [satellites, setSatellites] = useState([]);
    const [selectedSatName, setSelectedSatName] = useState("ISS (ZARYA)");
    const [fingerprint, setFingerprint] = useState(null);

    // Derived state for the selected satellite object
    const selectedSat = satellites.find(s => s.sat_name === selectedSatName) || satellites[0] || null;

    useEffect(() => {
        const fetchData = async () => {
            try {
                // 1. Fetch Log Events (Exclude high-frequency TLE noise)
                const logResponse = await axios.get(`/api/proxy/events/recent?limit=100&exclude_type=TLE_UPDATE`);
                setEvents(logResponse.data);

                // 2. Fetch Space Telemetry (Limit 200 to capture all 70+ sats)
                const spaceResponse = await axios.get(`/api/proxy/events/recent?limit=200&team=space`);

                // Process unique satellites
                const uniqueSats = {};
                let foundFingerprint = null;

                spaceResponse.data.forEach(event => {
                    if (event.event_type === 'FINGERPRINT_UPDATE') {
                        foundFingerprint = event.payload.image_b64;
                    }
                    if (event.event_type === 'TLE_UPDATE' && event.payload.sat_name) {
                        if (!uniqueSats[event.payload.sat_name]) {
                            uniqueSats[event.payload.sat_name] = event.payload;
                        }
                    }
                });

                setSatellites(Object.values(uniqueSats));
                if (foundFingerprint) setFingerprint(foundFingerprint);

            } catch (error) {
                console.error("Connection Error:", error);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, []);

    // Helper for Countdown
    const getCountdown = (nextPass) => {
        if (!nextPass || nextPass === "NO PASS < 24H") return "NO PASS < 24H";
        const diff = new Date(nextPass) - new Date();
        if (diff <= 0) return "ACQUIRING...";
        const hours = Math.floor(diff / 3600000);
        const minutes = Math.floor((diff % 3600000) / 60000);
        const seconds = Math.floor((diff % 60000) / 1000);
        return `T-MINUS ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    };

    return (
        <div className="min-h-screen bg-slate-950 text-cyan-400 font-mono p-6 selection:bg-cyan-900 selection:text-white">
            <WarHeader title="FUSION CENTER" subtitle="EXECUTIVE OVERSIGHT" />

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

                {/* COL 1: VISUALIZATIONS (4 cols) */}
                <div className="lg:col-span-4 space-y-6">

                    {/* SATELLITE MAP */}
                    <div className="h-[350px] border border-cyan-900/30 shadow-lg relative">
                        <SatelliteMap
                            satellites={satellites}
                            selectedSat={selectedSat}
                            fingerprint={fingerprint}
                        />
                        {/* Overlay: Target Selector */}
                        <div className="absolute top-2 left-2 z-[400]">
                            <select
                                value={selectedSatName}
                                onChange={(e) => setSelectedSatName(e.target.value)}
                                className="bg-slate-900/90 border border-cyan-500 text-cyan-400 text-xs p-1 rounded shadow-lg outline-none"
                            >
                                {satellites.sort((a, b) => a.sat_name.localeCompare(b.sat_name)).map(s => (
                                    <option key={s.sat_name} value={s.sat_name}>{s.sat_name}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {/* TELEMETRY CARD */}
                    <div className="bg-slate-900/50 p-4 border border-cyan-900/30 shadow-[0_0_15px_rgba(8,145,178,0.1)]">
                        <h3 className="text-xs text-cyan-600 mb-2 font-bold border-b border-cyan-900/30 pb-1 flex justify-between">
                            <span>PRIMARY TARGET TELEMETRY</span>
                            <span className="text-white">{selectedSat ? selectedSat.sat_name : "SEARCHING..."}</span>
                        </h3>

                        {selectedSat ? (
                            <div className="space-y-4">
                                {/* COUNTDOWN TIMER */}
                                <div className="bg-slate-950 p-3 border border-slate-800 text-center">
                                    <div className="text-slate-500 text-[10px] tracking-widest">NEXT ACQUISITION</div>
                                    <div className={`text-2xl font-black tracking-tighter ${selectedSat.visibility === 'VISIBLE' ? 'text-red-500 animate-pulse' : 'text-emerald-400'}`}>
                                        {selectedSat.visibility === 'VISIBLE' ? "TARGET ACQUIRED" : getCountdown(selectedSat.next_pass)}
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-2 text-center">
                                    <div className="bg-slate-950 p-2 border border-slate-800">
                                        <div className="text-[10px] text-slate-500">AZIMUTH</div>
                                        <div className="text-lg text-cyan-300">{selectedSat.azimuth}°</div>
                                    </div>
                                    <div className="bg-slate-950 p-2 border border-slate-800">
                                        <div className="text-[10px] text-slate-500">ELEVATION</div>
                                        <div className="text-lg text-cyan-300">{selectedSat.elevation}°</div>
                                    </div>
                                    <div className="bg-slate-950 p-2 border border-slate-800">
                                        <div className="text-[10px] text-slate-500">RANGE</div>
                                        <div className="text-lg text-white">{selectedSat.distance_km} km</div>
                                    </div>
                                    <div className="bg-slate-950 p-2 border border-slate-800">
                                        <div className="text-[10px] text-slate-500">ORIGIN</div>
                                        <div className="text-lg text-white">{selectedSat.origin_prediction?.country || "UNK"}</div>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="text-center py-8 text-slate-600 animate-pulse">WAITING FOR DOWNLINK...</div>
                        )}
                    </div>

                    <div className="bg-slate-900/50 p-4 border border-cyan-900/30">
                        <h3 className="text-xs text-cyan-600 mb-2 font-bold">ATTACK VELOCITY</h3>
                        <AttackChart events={events} />
                    </div>
                    <div className="bg-slate-900/50 p-4 border border-cyan-900/30">
                        <h3 className="text-xs text-cyan-600 mb-2 font-bold">NETWORK FLOW</h3>
                        <NetworkTrafficChart events={events} />
                    </div>
                </div>

                {/* COL 2: MASTER LOG (8 cols) */}
                <div className="lg:col-span-8 h-[800px]">
                    <EventLog events={events} title="UNIFIED BATTLESPACE FEED" />
                </div>

            </div>
        </div>
    );
}
