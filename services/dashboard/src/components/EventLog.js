import React from 'react';
import { format } from 'date-fns';

export default function EventLog({ events, title }) {
    return (
        <div className="bg-slate-900/50 border border-slate-800 rounded-sm flex flex-col shadow-lg h-full">
            <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-950/50">
                <h2 className="text-sm text-slate-400 font-bold tracking-widest uppercase">
                    {title || "Event Log"}
                </h2>
                <span className="text-[10px] text-slate-600">LIVE FEED</span>
            </div>

            <div className="overflow-y-auto flex-grow p-4 space-y-1 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-slate-950">
                <table className="w-full text-left text-xs border-collapse">
                    <thead className="sticky top-0 bg-slate-900 text-slate-500 border-b border-slate-700 z-10">
                        <tr>
                            <th className="pb-2 pl-2 font-normal w-24">TIME</th>
                            <th className="pb-2 font-normal w-32">MODULE</th>
                            <th className="pb-2 font-normal">DETAILS</th>
                            <th className="pb-2 font-normal text-right pr-2 w-20">SEV</th>
                        </tr>
                    </thead>
                    <tbody className="font-mono">
                        {events.map((event) => (
                            <tr key={event.id} className="border-b border-slate-800/50 hover:bg-white/5 transition-colors group">

                                {/* Timestamp */}
                                <td className="py-3 pl-2 text-slate-500 group-hover:text-white align-top">
                                    {format(new Date(event.timestamp), 'HH:mm:ss')}
                                </td>

                                {/* Module Name */}
                                <td className="py-3 align-top">
                                    <span className="bg-slate-800 text-slate-400 px-1 rounded text-[10px] border border-slate-700">
                                        {event.origin_module}
                                    </span>
                                </td>

                                {/* Event Type & Detail */}
                                <td className="py-3 align-top">
                                    <div className={`font-bold ${event.origin_module.startsWith('red.') ? 'text-red-500' :
                                            event.origin_module.startsWith('blue.') ? 'text-blue-400' :
                                                event.origin_module.startsWith('space.') ? 'text-emerald-400' :
                                                    'text-slate-300'
                                        }`}>
                                        {event.event_type}
                                    </div>

                                    <div className="text-[10px] text-slate-500 font-mono mt-1 break-all">
                                        {/* Smart Details Rendering */}
                                        {event.event_type === 'VULN_REPORT' && `PORT: ${event.payload?.port}/${event.payload?.service}`}
                                        {event.event_type === 'CREDENTIAL_CRACKED' && `USER: ${event.payload?.cracked_user} | PASS: ${event.payload?.weak_password}`}
                                        {event.event_type === 'AUTH_FAILURE' && `USER: ${event.payload?.username} | IP: ${event.context?.related_ip}`}
                                        {event.event_type === 'THREAT_DETECTED' && event.payload?.alert_title}
                                        {event.event_type === 'NETWORK_FLOW' && `${event.payload?.bytes_out} bytes -> ${event.context?.related_ip}`}
                                        {event.event_type === 'COMMAND_EXECUTED' && `$ ${event.payload?.command}`}
                                        {event.event_type === 'TLE_UPDATE' && `SAT: ${event.payload?.sat_name}`}
                                        {/* Fallback for generic events */}
                                        {!['VULN_REPORT', 'CREDENTIAL_CRACKED', 'AUTH_FAILURE', 'THREAT_DETECTED', 'NETWORK_FLOW', 'COMMAND_EXECUTED', 'TLE_UPDATE'].includes(event.event_type) &&
                                            JSON.stringify(event.payload).slice(0, 50)}
                                    </div>
                                </td>

                                {/* Severity Badge */}
                                <td className="py-3 text-right pr-2 align-top">
                                    <span className={`inline-block px-2 py-1 rounded-sm text-[10px] font-bold tracking-wider
                    ${event.severity === 'HIGH' ? 'bg-red-900/30 text-red-500 border border-red-900/50' :
                                            event.severity === 'CRITICAL' ? 'bg-red-600 text-white border border-red-500 animate-pulse' :
                                                event.severity === 'MEDIUM' ? 'bg-amber-900/30 text-amber-500 border border-amber-900/50' :
                                                    'bg-slate-800 text-slate-500 border border-slate-700'}`}>
                                        {event.severity}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {events.length === 0 && (
                    <div className="text-center text-slate-700 py-20 italic">
                        AWAITING TELEMETRY...
                    </div>
                )}
            </div>
        </div>
    );
}
