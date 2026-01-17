import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../context/AuthContext';

export default function Login() {
    const router = useRouter();
    const { login } = useAuth();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [target, setTarget] = useState(null);

    useEffect(() => {
        if (router.query.target) {
            setTarget(router.query.target);
        }
    }, [router.query]);

    const handleSubmit = (e) => {
        e.preventDefault();
        const result = login(username, password, target);
        if (!result.success) {
            setError(result.message);
            // Shake effect logic could go here
        }
    };

    return (
        <div className="min-h-screen bg-black font-mono flex items-center justify-center p-4">
            <div className="w-full max-w-md border border-slate-800 bg-slate-950/50 p-8 shadow-[0_0_50px_rgba(0,0,0,0.5)] relative overflow-hidden">

                {/* Scanline Effect */}
                <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] z-10 bg-[length:100%_2px,3px_100%]"></div>

                <div className="text-center mb-8 relative z-20">
                    <h1 className="text-3xl font-black text-white tracking-tighter mb-2">
                        ASTRA <span className="text-cyan-500">DYNAMICS</span>
                    </h1>
                    <p className="text-xs text-slate-500 tracking-[0.3em] uppercase">
                        Secure Access Terminal v4.0
                    </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6 relative z-20">
                    <div>
                        <label className="block text-xs text-cyan-500 mb-1 tracking-widest">IDENTITY</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="w-full bg-slate-900 border border-slate-700 text-white p-3 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all placeholder-slate-700"
                            placeholder="ENTER USERNAME"
                            autoFocus
                        />
                    </div>

                    <div>
                        <label className="block text-xs text-cyan-500 mb-1 tracking-widest">PASSPHRASE</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full bg-slate-900 border border-slate-700 text-white p-3 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all placeholder-slate-700"
                            placeholder="••••••••"
                        />
                    </div>

                    {error && (
                        <div className="text-red-500 text-xs text-center font-bold animate-pulse border border-red-900/50 bg-red-950/30 p-2">
                            ⚠️ {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        className="w-full bg-cyan-900/20 border border-cyan-500/50 text-cyan-400 py-3 font-bold hover:bg-cyan-500 hover:text-black transition-all duration-300 tracking-widest text-sm"
                    >
                        AUTHENTICATE
                    </button>
                </form>

                <div className="mt-8 text-center relative z-20">
                    <p className="text-[10px] text-slate-700">
                        UNAUTHORIZED ACCESS IS A FEDERAL OFFENSE.<br />
                        ALL ACTIVITY IS LOGGED AND MONITORED.
                    </p>
                </div>

            </div>
        </div>
    );
}
