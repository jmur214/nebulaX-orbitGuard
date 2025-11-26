import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function NetworkTrafficChart({ events }) {
    // Aggregate bytes out by country
    const data = React.useMemo(() => {
        const countryStats = {};

        events.forEach(e => {
            // Check for NETWORK_FLOW or any event with bytes_out
            if (e.payload && (e.payload.destination_country || e.payload.bytes_out)) {
                const country = e.payload.destination_country || 'UNKNOWN';
                const bytes = parseInt(e.payload.bytes_out || 0, 10);
                if (bytes > 0) {
                    countryStats[country] = (countryStats[country] || 0) + bytes;
                }
            }
        });

        return Object.keys(countryStats).map(key => ({
            country: key,
            bytes: countryStats[key]
        })).sort((a, b) => b.bytes - a.bytes).slice(0, 5); // Top 5
    }, [events]);

    return (
        <div className="h-[200px] w-full bg-slate-900/50 border border-cyan-900/50 p-4 rounded-sm">
            <h3 className="text-xs text-cyan-400 font-bold mb-2 tracking-widest border-b border-cyan-900/30 pb-2">
                DATA EXFILTRATION // BY DESTINATION
            </h3>
            {data.length === 0 ? (
                <div className="h-full flex items-center justify-center text-slate-600 text-xs">NO TRAFFIC DETECTED</div>
            ) : (
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                        <XAxis type="number" stroke="#64748b" fontSize={10} tickFormatter={(val) => `${(val / 1000).toFixed(0)}k`} />
                        <YAxis dataKey="country" type="category" stroke="#64748b" fontSize={10} width={30} />
                        <Tooltip
                            cursor={{ fill: '#1e293b' }}
                            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }}
                        />
                        <Bar dataKey="bytes" fill="#06b6d4" radius={[0, 4, 4, 0]}>
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={index === 0 ? '#ef4444' : '#06b6d4'} />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            )}
        </div>
    );
}
