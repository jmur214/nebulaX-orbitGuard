import React, { useState, useEffect } from 'react';
import axios from 'axios';
import WarHeader from '../components/WarHeader';
import EventLog from '../components/EventLog';
import AttackChart from '../components/AttackChart';

export default function RedTeam() {
    const [events, setEvents] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get(`/api/proxy/events/recent?limit=50&team=red`);
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
        <div className="min-h-screen bg-black text-red-500 font-mono p-6 selection:bg-red-900 selection:text-white">
            <WarHeader title="THE SYNDICATE" subtitle="RED TEAM OPERATIONS" />

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* LEFT COL: ATTACK METRICS */}
                <div className="lg:col-span-4 space-y-6">
                    <div className="bg-red-950/20 border border-red-900/50 p-6 rounded-sm">
                        <h2 className="text-xl font-bold text-red-500 mb-4 border-b border-red-900 pb-2">CAMPAIGN STATUS</h2>
                        <div className="space-y-4">
                            <div className="flex justify-between">
                                <span className="text-red-400">TARGET:</span>
                                <span className="text-white font-bold">ASTRA DYNAMICS</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-red-400">OBJECTIVE:</span>
                                <span className="text-white font-bold">EXFILTRATE ORION BLUEPRINTS</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-red-400">ACTIVE NODES:</span>
                                <span className="text-white font-bold animate-pulse">5</span>
                            </div>
                        </div>
                    </div>

                    <AttackChart events={events} />
                </div>

                {/* RIGHT COL: EVENT LOG */}
                <div className="lg:col-span-8 h-[700px]">
                    <EventLog events={events} title="ATTACK LOGS" />
                </div>
            </div>
        </div>
    );
}
