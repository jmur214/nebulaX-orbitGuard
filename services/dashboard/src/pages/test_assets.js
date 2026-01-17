import React from 'react';

export default function TestAssets() {
    return (
        <div className="p-10 bg-slate-900 min-h-screen text-white font-mono">
            <h1 className="text-2xl text-emerald-400 mb-6">ASSET INTEGRITY CHECK</h1>

            <div className="grid grid-cols-2 gap-8">
                {/* 1. Base Texture Check */}
                <div className="border border-slate-700 p-4">
                    <h2 className="text-xl mb-4">1. Earth Texture Tile</h2>
                    <p className="text-sm text-slate-400 mb-2">Path: /cesium/Assets/Textures/NaturalEarthII/2/0/0.jpg</p>
                    <div className="bg-checkered p-2 inline-block">
                        <img
                            src="/cesium/Assets/Textures/NaturalEarthII/2/0/0.jpg"
                            alt="Earth Tile"
                            width={256}
                            height={128}
                            className="border border-red-500"
                        />
                    </div>
                    <p className="mt-2 text-xs text-orange-400">If this image is broken, the Globe CANNOT render.</p>
                </div>

                {/* 2. Widget Icon Check */}
                <div className="border border-slate-700 p-4">
                    <h2 className="text-xl mb-4">2. UI Widget Icon</h2>
                    <p className="text-sm text-slate-400 mb-2">Path: /cesium/Widgets/Images/NavigationHelp/MouseLeft.svg</p>
                    <div className="bg-white p-2 inline-block">
                        <img
                            src="/cesium/Widgets/Images/NavigationHelp/MouseLeft.svg"
                            alt="Mouse Icon"
                            width={50}
                            height={50}
                            className="border border-red-500"
                        />
                    </div>
                </div>

                {/* 3. CSS Check */}
                <div className="border border-slate-700 p-4 col-span-2">
                    <h2 className="text-xl mb-4">3. CSS Availability</h2>
                    <p className="text-sm text-slate-400 mb-2">Iframe loading: /cesium/Widgets/widgets.css</p>
                    <iframe
                        src="/cesium/Widgets/widgets.css"
                        className="w-full h-32 bg-white text-black"
                    />
                    <p className="mt-2 text-xs text-orange-400">If this says "404" or shows a Next.js error page, styles are missing.</p>
                </div>
            </div>

            <div className="mt-8 p-4 bg-slate-800 rounded">
                <h3 className="font-bold text-emerald-400">DIAGNOSIS GUIDE:</h3>
                <ul className="list-disc pl-6 space-y-2 mt-2">
                    <li><strong className="text-green-400">IMAGES VISIBLE:</strong> The problem is inside Cesium (Code/Logic).</li>
                    <li><strong className="text-red-400">BROKEN IMAGES:</strong> The problem is Docker/Next.js (File System/Mounting).</li>
                </ul>
            </div>
        </div>
    );
}
