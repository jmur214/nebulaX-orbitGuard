import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function WarHeader({ title, subtitle }) {
    const [gameState, setGameState] = useState({
        defcon: 5,
        red_score: 0,
        blue_score: 0,
        status: "LOADING..."
    });

    useEffect(() => {
        const fetchState = async () => {
            try {
                // Same-origin via Next.js rewrite (see next.config.js rewrites()).
                // Avoids CORS / cross-port-forwarding issues in Codespaces.
                const response = await axios.get(`/api/proxy/game/state`);
                setGameState(response.data);
            } catch (error) {
                console.error("Game State Error:", error);
            }
        };

        fetchState();
        const interval = setInterval(fetchState, 5000);
        return () => clearInterval(interval);
    }, []);

    // Calculate percentage for the tug-of-war bar
    const totalScore = gameState.red_score + gameState.blue_score;
    const redPercent = totalScore === 0 ? 50 : (gameState.red_score / totalScore) * 100;

    return (
        <header className="mb-8 border-b border-slate-800 pb-4">
            <div className="flex justify-between items-end mb-4">
                <div>
                    <h1 className="text-4xl font-black tracking-tighter text-white mb-1">
                        ASTRA <span className="text-cyan-500">DYNAMICS</span>
                    </h1>
                    <p className="text-xs text-slate-500 tracking-[0.3em] uppercase">
                        {title} // {subtitle}
                    </p>
                </div>

                <div className="text-right">
                    <div className={`text-2xl font-black tracking-widest ${gameState.defcon === 1 ? 'text-red-600 animate-pulse' :
                            gameState.defcon === 2 ? 'text-red-500' :
                                gameState.defcon === 3 ? 'text-amber-500' :
                                    gameState.defcon === 4 ? 'text-green-500' : 'text-blue-500'
                        }`}>
                        DEFCON {gameState.defcon}
                    </div>
                    <div className="text-[10px] text-slate-600 uppercase">Current Threat Level</div>
                </div>
            </div>

            {/* TUG OF WAR BAR */}
            <div className="w-full h-4 bg-slate-900 rounded-full overflow-hidden flex border border-slate-700 relative">
                {/* Red Bar */}
                <div
                    className="h-full bg-red-900/80 transition-all duration-1000 flex items-center justify-start pl-2 text-[10px] text-red-300 font-bold"
                    style={{ width: `${redPercent}%` }}
                >
                    RED: {gameState.red_score}
                </div>

                {/* Blue Bar */}
                <div
                    className="h-full bg-blue-900/80 transition-all duration-1000 flex items-center justify-end pr-2 text-[10px] text-blue-300 font-bold"
                    style={{ width: `${100 - redPercent}%` }}
                >
                    BLUE: {gameState.blue_score}
                </div>

                {/* Center Marker */}
                <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-white/20 -translate-x-1/2"></div>
            </div>
        </header>
    );
}
