/** @type {import('next').NextConfig} */
const path = require('path');

const nextConfig = {
    reactStrictMode: false, // DISABLED - testing if double-mount breaks Cesium
    transpilePackages: ['resium'],
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
