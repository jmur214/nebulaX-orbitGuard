import { useState, useEffect } from 'react';
import axios from 'axios';
import { format } from 'date-fns';
import dynamic from 'next/dynamic';
import AttackChart from '../components/AttackChart';
import NetworkTrafficChart from '../components/NetworkTrafficChart';

// --- NEW: Dynamic Import for the Map ---
// We use 'dynamic' to prevent server-side rendering errors with the Leaflet library
const SatelliteMap = dynamic(() => import('../components/SatelliteMap'), {
  ssr: false,
  loading: () => <div className="h-[350px] w-full bg-slate-900 animate-pulse text-cyan-800 flex items-center justify-center">LOADING MAP DATA...</div>
});

export default function Dashboard() {
  const [events, setEvents] = useState([]);
  const [telemetry, setTelemetry] = useState(null);

  // Polling Logic
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Use localhost for browser-side fetching
        // Increased limit to 100 to ensure we capture Red Team events amidst frequent TLE updates
        const API_HOST = process.env.NEXT_PUBLIC_API_HOST || 'http://localhost:8000';
        const response = await axios.get(`${API_HOST}/events/recent?limit=100`);
        const data = response.data;
        setEvents(data);

        // Extract latest space telemetry
        const latestSpace = data.find(e => e.origin_module === 'space.tracker');
        if (latestSpace) {
          setTelemetry(latestSpace.payload);
        }
      } catch (error) {
        console.error("Connection Error:", error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-cyan-500 font-mono p-6 selection:bg-cyan-900 selection:text-white">

      {/* --- HEADER --- */}
      <header className="mb-8 border-b border-cyan-900/50 pb-4 flex justify-between items-end">
        <div>
          <h1 className="text-5xl font-black tracking-tighter text-white mb-1">
            NEBULA<span className="text-cyan-500">X</span>
          </h1>
          <p className="text-xs text-cyan-700 tracking-[0.3em]">ORBITGUARD DEFENSE MATRIX // v2.4.0</p>
        </div>
        <div className="text-right hidden md:block">
          <div className="text-xs text-emerald-500 animate-pulse">● SYSTEM ONLINE</div>
          <div className="text-xs text-slate-500">SECURE CONNECTION ESTABLISHED</div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* --- COL 1: SATELLITE TELEMETRY (4 Columns wide) --- */}
        <div className="lg:col-span-4 space-y-6">

          {/* --- NEW: 2D MAP COMPONENT --- */}
          {/* This sits on top of the data card for maximum visual impact */}
          <div className="shadow-[0_0_20px_rgba(8,145,178,0.2)]">
            <SatelliteMap telemetry={telemetry} />
          </div>

          {/* Status Card */}
          <div className="bg-slate-900/50 border border-cyan-900/50 p-6 rounded-sm shadow-[0_0_15px_rgba(8,145,178,0.1)]">
            <h2 className="text-sm text-cyan-400 font-bold border-b border-cyan-800 pb-2 mb-4 tracking-widest">
              SAT-LINK // TELEMETRY
            </h2>

            {!telemetry ? (
              <div className="text-center py-10 text-cyan-800 animate-pulse">
                SEARCHING FOR SIGNAL...
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-slate-500 text-xs">TARGET ASSET</span>
                  <span className="text-white font-bold text-lg">{telemetry.sat_name}</span>
                </div>

                <div className="grid grid-cols-2 gap-4 mt-4">
                  <div className="bg-slate-950 p-3 border border-slate-800">
                    <div className="text-slate-500 text-[10px]">AZIMUTH</div>
                    <div className="text-xl text-cyan-300">{telemetry.azimuth}°</div>
                  </div>
                  <div className="bg-slate-950 p-3 border border-slate-800">
                    <div className="text-slate-500 text-[10px]">ELEVATION</div>
                    <div className="text-xl text-cyan-300">{telemetry.elevation}°</div>
                  </div>
                </div>

                {/* --- NEXT PASS PREDICTION --- */}
                <div className="bg-slate-950 p-3 border border-slate-800">
                  <div className="text-slate-500 text-[10px]">NEXT ACQUISITION (UTC)</div>
                  <div className="text-lg text-emerald-400 font-mono font-bold">
                    {telemetry.next_pass && telemetry.next_pass !== "NO PASS < 24H"
                      ? format(new Date(telemetry.next_pass), 'HH:mm:ss')
                      : <span className="text-amber-500 text-sm">NO PASS &lt; 24H</span>
                    }
                  </div>
                </div>

                <div className="bg-slate-950 p-3 border border-slate-800">
                  <div className="text-slate-500 text-[10px]">SLANT RANGE</div>
                  <div className="text-xl text-white">{telemetry.distance_km} <span className="text-sm text-slate-600">km</span></div>
                </div>

                {/* Visibility Status Box */}
                <div className={`mt-4 p-3 text-center border border-dashed tracking-widest font-bold transition-colors duration-500
                  ${telemetry.visibility === 'VISIBLE'
                    ? 'bg-red-950/30 border-red-500 text-red-500 animate-pulse shadow-[0_0_20px_rgba(220,38,38,0.2)]'
                    : 'bg-slate-900 border-slate-700 text-slate-600'}`}>
                  {telemetry.visibility === 'VISIBLE' ? '⚠ TARGET ACQUIRED' : '// BELOW HORIZON'}
                </div>
              </div>
            )}
          </div>

          {/* Decorative "Systems" Box */}
          <div className="bg-slate-900/30 border border-slate-800 p-4 rounded-sm opacity-75">
            <h3 className="text-xs text-slate-500 mb-2">SUBSYSTEMS</h3>
            <div className="grid grid-cols-3 gap-2 text-[10px] text-center">
              <div className="bg-emerald-900/20 text-emerald-600 border border-emerald-900/30 py-1">PHYSICS: OK</div>
              <div className="bg-emerald-900/20 text-emerald-600 border border-emerald-900/30 py-1">DB: ONLINE</div>
              <div className="bg-amber-900/20 text-amber-600 border border-amber-900/30 py-1 animate-pulse">RED TEAM: ACTIVE</div>
            </div>
          </div>

          {/* --- NEW: CHARTS SECTION --- */}
          <AttackChart events={events} />
          <NetworkTrafficChart events={events} />
        </div>

        {/* --- COL 2: EVENT LOG (8 Columns wide) --- */}
        <div className="lg:col-span-8 bg-slate-900/50 border border-cyan-900/50 rounded-sm flex flex-col shadow-[0_0_15px_rgba(8,145,178,0.1)]">
          <div className="p-4 border-b border-cyan-900/50 flex justify-between items-center">
            <h2 className="text-sm text-cyan-400 font-bold tracking-widest">
              CENTRAL EVENT BUS // LIVE FEED
            </h2>
            <span className="text-[10px] text-slate-600">POLLING RATE: 5000ms</span>
          </div>

          <div className="overflow-y-auto h-[600px] p-4 space-y-1 scrollbar-thin scrollbar-thumb-cyan-900 scrollbar-track-slate-950">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="sticky top-0 bg-slate-900 text-slate-500 border-b border-slate-700">
                <tr>
                  <th className="pb-2 pl-2 font-normal">TIME (UTC)</th>
                  <th className="pb-2 font-normal">MODULE</th>
                  <th className="pb-2 font-normal">EVENT TYPE & DETAILS</th>
                  <th className="pb-2 font-normal text-right pr-2">SEVERITY</th>
                </tr>
              </thead>
              <tbody className="font-mono">
                {events.map((event) => (
                  <tr key={event.id} className="border-b border-slate-800/50 hover:bg-cyan-900/10 transition-colors group">

                    {/* Timestamp */}
                    <td className="py-3 pl-2 text-slate-500 group-hover:text-cyan-400 align-top">
                      {format(new Date(event.timestamp), 'HH:mm:ss')}
                    </td>

                    {/* Module Name */}
                    <td className="py-3 align-top">
                      <span className="bg-slate-800 text-slate-300 px-1 rounded text-[10px] border border-slate-700">
                        {event.origin_module}
                      </span>
                    </td>

                    {/* Event Type & Detail Column (UPDATED LOGIC) */}
                    <td className="py-3 align-top">
                      <div className={`font-bold ${event.origin_module.startsWith('red.') ? 'text-red-500' :
                        event.origin_module.startsWith('blue.') ? 'text-blue-400' :
                          event.origin_module.startsWith('space.') ? 'text-white' :
                            'text-cyan-300'
                        }`}>
                        {event.event_type}
                      </div>

                      {/* SMART DETAILS: Show context based on event type */}
                      <div className="text-[10px] text-slate-500 font-mono mt-1">
                        {event.event_type === 'VULN_REPORT' && (
                          <span>OPEN PORT: {event.payload?.port}/{event.payload?.service}</span>
                        )}
                        {event.event_type === 'CREDENTIAL_CRACKED' && (
                          <span className="text-amber-400">USER: {event.payload?.cracked_user} | PASS: {event.payload?.weak_password}</span>
                        )}
                        {event.event_type === 'AUTH_FAILURE' && (
                          <span>USER: {event.payload?.username} | IP: {event.context?.related_ip}</span>
                        )}
                        {event.event_type === 'THREAT_DETECTED' && (
                          <span className="text-red-400 font-bold">{event.payload?.alert_title}</span>
                        )}
                        {event.event_type === 'NETWORK_FLOW' && (
                          <span>DEST: {event.context?.related_ip} | {event.payload?.bytes_out} bytes</span>
                        )}
                        {event.event_type === 'COMMAND_EXECUTED' && (
                          <span className="text-green-400">$ {event.payload?.command}</span>
                        )}
                      </div>
                    </td>

                    {/* Severity Badge */}
                    <td className="py-3 text-right pr-2 align-top">
                      <span className={`inline-block px-2 py-1 rounded-sm text-[10px] font-bold tracking-wider
                        ${event.severity === 'HIGH' ? 'bg-red-500/20 text-red-400 border border-red-900/50' :
                          event.severity === 'CRITICAL' ? 'bg-red-900/50 text-red-200 border border-red-500 animate-pulse' :
                            event.severity === 'MEDIUM' ? 'bg-amber-500/20 text-amber-400 border border-amber-900/50' :
                              'bg-cyan-500/10 text-cyan-600 border border-cyan-900/30'}`}>
                        {event.severity}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {events.length === 0 && (
              <div className="text-center text-slate-600 py-20">NO EVENTS DETECTED</div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}