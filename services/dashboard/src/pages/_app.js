import '../styles/globals.css';
import { AuthProvider } from '../context/AuthContext';
// Import Cesium widgets CSS globally to ensure correct rendering
import "cesium/Build/Cesium/Widgets/widgets.css";

// CRITICAL: Set Cesium configuration BEFORE any Cesium code runs
// This MUST happen before any component imports Cesium or Resium
if (typeof window !== 'undefined') {
  window.CESIUM_BASE_URL = '/cesium';

  // Import Cesium and set the Ion token IMMEDIATELY
  // This must happen synchronously before any Viewer is created
  const Cesium = require('cesium');

  // Set your personal Cesium Ion access token
  Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI5MzNlOWUyMS0wNjJkLTRjNDktYmViNy1hZDg1MzEzMDAyYTkiLCJpZCI6Mzc5NTQ2LCJpYXQiOjE3Njg1NDgwODd9.80xIDuR1RDjlanpuPp7inELKaHyUnF302Jg4wfN8ne0';

  console.log("=== _app.js: Cesium configured ===");
  console.log("CESIUM_BASE_URL:", window.CESIUM_BASE_URL);
  console.log("Ion.defaultAccessToken set:", Cesium.Ion.defaultAccessToken.substring(0, 30) + "...");
}

function MyApp({ Component, pageProps }) {
  return (
    <AuthProvider>
      <Component {...pageProps} />
    </AuthProvider>
  );
}

export default MyApp;