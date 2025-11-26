import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function AttackChart({ events }) {
    // Aggregate events by minute
    const data = React.useMemo(() => {
        const counts = {};

        if (events.length === 0) return [];

        // 1. Group all events by HH:mm
        events.forEach(e => {
            const t = new Date(e.timestamp);
            const key = t.toISOString().substring(11, 16); // HH:mm
            counts[key] = (counts[key] || 0) + 1;
        });

        // 2. Determine the range based on the LATEST event, not browser time
        // This handles clock skew where server time > browser time
        const sortedKeys = Object.keys(counts).sort();
        if (sortedKeys.length === 0) return [];

        const lastKey = sortedKeys[sortedKeys.length - 1];
        // Create a Date object for the last key (using today's date for simplicity as we only care about time)
        const now = new Date();
        const [h, m] = lastKey.split(':').map(Number);
        now.setUTCHours(h, m, 0, 0);

        const finalData = [];
        // Generate last 10 minutes ending at the latest event time
        for (let i = 9; i >= 0; i--) {
            const t = new Date(now.getTime() - i * 60000);
            const key = t.toISOString().substring(11, 16);
            finalData.push({
                time: key,
                attacks: counts[key] || 0
            });
        }

        return finalData;
    }, [events]);

    return (
        <div className="h-[200px] w-full bg-slate-900/50 border border-cyan-900/50 p-4 rounded-sm">
            <h3 className="text-xs text-cyan-400 font-bold mb-2 tracking-widest border-b border-cyan-900/30 pb-2">
                THREAT VOLUME // LAST 10 MIN
            </h3>
            {/* Chart Container */}

            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data}>
                    <defs>
                        <linearGradient id="colorAttacks" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="time" stroke="#64748b" fontSize={10} tickLine={false} />
                    <YAxis stroke="#64748b" fontSize={10} tickLine={false} />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }}
                        itemStyle={{ color: '#ef4444' }}
                    />
                    <Area type="monotone" dataKey="attacks" stroke="#ef4444" fillOpacity={1} fill="url(#colorAttacks)" />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}
