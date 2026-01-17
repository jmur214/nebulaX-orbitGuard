import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuth } from '../context/AuthContext';

export default function MissionSelect() {
  const { user } = useAuth();
  const router = useRouter();

  const handleModuleClick = (e, targetRoute, requiredRole) => {
    e.preventDefault();

    // If logged in and has correct role (or is Fusion director), go through
    if (user && (user.role === requiredRole || user.role === 'FUSION')) {
      router.push(targetRoute);
    } else {
      // Otherwise, go to login with target
      router.push(`/login?target=${targetRoute}`);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center font-mono p-4">

      <div className="text-center mb-12">
        <h1 className="text-6xl font-black text-white tracking-tighter mb-2">
          ASTRA <span className="text-cyan-500">DYNAMICS</span>
        </h1>
        <p className="text-slate-500 tracking-[0.5em] text-sm uppercase">
          Cyber-Physical Wargame Platform
        </p>
        {user && (
          <div className="mt-4 text-emerald-500 text-xs tracking-widest border border-emerald-900/50 bg-emerald-950/20 inline-block px-4 py-1 rounded-full">
            IDENTITY VERIFIED: {user.username.toUpperCase()} // {user.role}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl w-full">

        {/* RED TEAM */}
        <div onClick={(e) => handleModuleClick(e, '/red', 'RED_TEAM')} className="cursor-pointer group relative overflow-hidden bg-red-950/20 border border-red-900/50 p-8 hover:bg-red-900/40 transition-all duration-300 hover:scale-[1.02]">
          <div className="absolute top-0 right-0 p-4 opacity-20 group-hover:opacity-50 transition-opacity">
            <svg className="w-16 h-16 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
          </div>
          <h2 className="text-2xl font-bold text-red-500 mb-2">RED TEAM</h2>
          <p className="text-red-300/60 text-sm">The Syndicate. Offensive Operations. Breach the perimeter.</p>
        </div>

        {/* BLUE TEAM */}
        <div onClick={(e) => handleModuleClick(e, '/blue', 'BLUE_TEAM')} className="cursor-pointer group relative overflow-hidden bg-blue-950/20 border border-blue-900/50 p-8 hover:bg-blue-900/40 transition-all duration-300 hover:scale-[1.02]">
          <div className="absolute top-0 right-0 p-4 opacity-20 group-hover:opacity-50 transition-opacity">
            <svg className="w-16 h-16 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>
          </div>
          <h2 className="text-2xl font-bold text-blue-400 mb-2">BLUE TEAM</h2>
          <p className="text-blue-300/60 text-sm">Astra SecOps. Defense Center. Detect and contain.</p>
        </div>

        {/* SPACE COMMAND */}
        <div onClick={(e) => handleModuleClick(e, '/space', 'SPACE_CMD')} className="cursor-pointer group relative overflow-hidden bg-emerald-950/20 border border-emerald-900/50 p-8 hover:bg-emerald-900/40 transition-all duration-300 hover:scale-[1.02]">
          <div className="absolute top-0 right-0 p-4 opacity-20 group-hover:opacity-50 transition-opacity">
            <svg className="w-16 h-16 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path></svg>
          </div>
          <h2 className="text-2xl font-bold text-emerald-400 mb-2">SPACE COMMAND</h2>
          <p className="text-emerald-300/60 text-sm">OrbitGuard. Telemetry & Physics. Maintain the link.</p>
        </div>

        {/* FUSION CENTER */}
        <div onClick={(e) => handleModuleClick(e, '/fusion', 'FUSION')} className="cursor-pointer group relative overflow-hidden bg-purple-950/20 border border-purple-900/50 p-8 hover:bg-purple-900/40 transition-all duration-300 hover:scale-[1.02]">
          <div className="absolute top-0 right-0 p-4 opacity-20 group-hover:opacity-50 transition-opacity">
            <svg className="w-16 h-16 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path></svg>
          </div>
          <h2 className="text-2xl font-bold text-purple-400 mb-2">FUSION CENTER</h2>
          <p className="text-purple-300/60 text-sm">Executive Oversight. God View. Total situational awareness.</p>
        </div>

      </div>


      <div className="mt-12 text-slate-600 text-xs">
        SECURE TERMINAL // AUTHORIZED PERSONNEL ONLY
      </div>
    </div>
  );
}