import React, { useState, useEffect } from 'react';
import axios from 'axios';
import WarHeader from '../components/WarHeader';
import EventLog from '../components/EventLog';
import NetworkTrafficChart from '../components/NetworkTrafficChart';

export default function BlueTeam() {
    const [events, setEvents] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get(`/api/proxy/events/recent?limit=50&team=blue`);
                setEvents(response.data);
            } catch (error) {
                console.error("Connection Error:", error);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="min-h-screen bg-slate-950 text-blue-400 font-mono p-6 selection:bg-blue-900 selection:text-white">
            <WarHeader title="ASTRA SECOPS" subtitle="BLUE TEAM DEFENSE" />

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* LEFT COL: DEFENSE METRICS */}
                <div className="lg:col-span-4 space-y-6">
                    <div className="bg-blue-950/20 border border-blue-900/50 p-6 rounded-sm">
                        <h2 className="text-xl font-bold text-blue-400 mb-4 border-b border-blue-900 pb-2">SYSTEM HEALTH</h2>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-slate-900 p-3 border border-slate-800 text-center">
                                <div className="text-xs text-slate-500">FIREWALL</div>
                                <div className="text-emerald-500 font-bold">ACTIVE</div>
                            </div>
                            <div className="bg-slate-900 p-3 border border-slate-800 text-center">
                                <div className="text-xs text-slate-500">IDS SENSORS</div>
                                <div className="text-emerald-500 font-bold">ONLINE</div>
                            </div>
                            <div className="bg-slate-900 p-3 border border-slate-800 text-center">
                                <div className="text-xs text-slate-500">HONEYPOTS</div>
                                <div className="text-amber-500 font-bold">ENGAGED</div>
                            </div>
                            <div className="bg-slate-900 p-3 border border-slate-800 text-center">
                                <div className="text-xs text-slate-500">THREAT LEVEL</div>
                                <div className="text-red-500 font-bold animate-pulse">ELEVATED</div>
                            </div>
                        </div>
                    </div>

                    <NetworkTrafficChart events={events} />
                </div>

                {/* RIGHT COL: EVENT LOG */}
                <div className="lg:col-span-8 h-[700px]">
                    <EventLog events={events} title="SECURITY ALERTS" />
                </div>
            </div>
        </div>
    );
}
