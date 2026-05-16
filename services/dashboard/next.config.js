/** @type {import('next').NextConfig} */
const path = require('path');

const nextConfig = {
    // Cesium's Viewer attaches a global WebGL context and cannot survive React 18's
    // StrictMode double-invoke pattern. Keep this OFF unless you're prepared to rebuild
    // SatelliteGlobe.js around the `done.current` guard in its Setup component.
    reactStrictMode: false,
    transpilePackages: ['resium'],

    // Proxy /api/proxy/* through Next.js to the core API. This means the browser
    // only ever talks to the same origin (port 3000), avoiding CORS and the
    // Codespaces "private port forward auth-bounce" problem entirely. Set
    // CORE_API_INTERNAL to override the upstream (default localhost:8000 works
    // for both ./dev.sh and Codespaces — the codespace VM has the docker-compose
    // 8000:8000 host mapping).
    async rewrites() {
        const upstream = process.env.CORE_API_INTERNAL || 'http://localhost:8000';
        return [
            { source: '/api/proxy/:path*', destination: `${upstream}/:path*` },
        ];
    },

    webpack: (config, { webpack }) => {
        config.plugins.push(
            new webpack.DefinePlugin({
                CESIUM_BASE_URL: JSON.stringify('/cesium'),
            })
        );
        // Fix for the @zip.js/zip.js "exports" issue in Cesium 1.109+
        config.resolve.exportsFields = [];
        // Explicit Alias to MOCK file because zip-no-worker.js does not exist in this version
        config.resolve.alias['@zip.js/zip.js/lib/zip-no-worker.js'] = path.join(__dirname, 'src/lib/zip-mock.js');

        return config;
    },
};

module.exports = nextConfig;
