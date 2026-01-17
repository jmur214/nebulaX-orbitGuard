import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, Polyline, Circle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default Leaflet icon markers in Next.js
const icon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41]
});

// Satellite Icon (Cyan Dot)
const satIcon = L.divIcon({
  className: 'custom-div-icon',
  html: "<div style='background-color: #06b6d4; width: 12px; height: 12px; border-radius: 50%; box-shadow: 0 0 10px #06b6d4; border: 2px solid white;'></div>",
  iconSize: [12, 12],
  iconAnchor: [6, 6]
});

// Helper component to programmatically move the map when data updates
function MapController({ center }) {
  const map = useMap();
  useEffect(() => {
    if (center[0] !== 0 && center[1] !== 0) {
      map.setView(center, map.getZoom());
    }
  }, [center, map]);
  return null;
}

export default function SatelliteMap({ satellites, selectedSat, fingerprint, onSatelliteSelect }) {
  const [showFingerprint, setShowFingerprint] = React.useState(false);

  // Center on selected satellite, or first one, or [0,0]
  const center = selectedSat
    ? [selectedSat.geo_lat, selectedSat.geo_lng]
    : (satellites && satellites.length > 0)
      ? [satellites[0].geo_lat, satellites[0].geo_lng]
      : [0, 0];

  // Helper to get color by country
  const getCountryColor = (country) => {
    switch (country) {
      case 'USA': return '#3b82f6'; // Blue
      case 'RUSSIA': return '#ef4444'; // Red
      case 'CHINA': return '#eab308'; // Yellow
      case 'ESA': return '#10b981'; // Green
      default: return '#94a3b8'; // Gray
    }
  };

  return (
    <div className="h-[350px] w-full rounded-sm overflow-hidden border border-cyan-900/50 bg-slate-900 relative z-0">
      <MapContainer
        center={center}
        zoom={2}
        scrollWheelZoom={false}
        style={{ height: '100%', width: '100%', background: '#0f172a' }}
      >
        {/* Dark Matter Map Tiles */}
        <TileLayer
          attribution='&copy; OpenStreetMap'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {/* Auto-center the map when selected satellite moves */}
        <MapController center={center} />

        {/* Render All Satellites */}
        {satellites && satellites.map((sat) => {
          const isSelected = selectedSat && selectedSat.sat_name === sat.sat_name;
          return (
            <React.Fragment key={sat.sat_name}>
              {/* Draw Path & Footprint ONLY for Selected Satellite */}
              {isSelected && sat.orbit_path && (
                <>
                  <Polyline
                    positions={sat.orbit_path}
                    pathOptions={{ color: '#06b6d4', weight: 2, opacity: 0.8, dashArray: '5, 10' }}
                  />
                  <Circle
                    center={[sat.geo_lat, sat.geo_lng]}
                    radius={2500000}
                    pathOptions={{ color: '#06b6d4', fillColor: '#06b6d4', fillOpacity: 0.1, weight: 1 }}
                  />
                </>
              )}

              <Marker
                position={[sat.geo_lat, sat.geo_lng]}
                eventHandlers={{
                  click: () => onSatelliteSelect && onSatelliteSelect(sat)
                }}
                icon={L.divIcon({
                  className: 'custom-div-icon',
                  html: `<div style='background-color: ${isSelected ? '#ffffff' : getCountryColor(sat.origin_prediction?.country)}; width: ${isSelected ? '14px' : '8px'}; height: ${isSelected ? '14px' : '8px'}; border-radius: 50%; box-shadow: 0 0 ${isSelected ? '15px #ffffff' : '5px ' + getCountryColor(sat.origin_prediction?.country)}; border: ${isSelected ? '2px solid #06b6d4' : '1px solid white'}; cursor: pointer;'></div>`,
                  iconSize: [14, 14],
                  iconAnchor: [7, 7]
                })}
                zIndexOffset={isSelected ? 1000 : 0}
              >
                {/* Popup Removed for Dashboard Integration */}
              </Marker>
            </React.Fragment>
          );
        })}

        {/* Ground Station (Green Dot) */}
        <Marker position={[41.8952, -87.8257]} icon={L.divIcon({
          html: "<div style='background-color: #10b981; width: 10px; height: 10px; border-radius: 50%; box-shadow: 0 0 10px #10b981;'></div>",
          className: ''
        })}>
          <Popup>GROUND STATION ALPHA (Chicago)</Popup>
        </Marker>

      </MapContainer>

      {/* Overlay Controls */}
      <div className="absolute top-2 right-2 z-[1000]">
        <button
          onClick={() => setShowFingerprint(true)}
          className="bg-slate-900/80 border border-cyan-500 text-cyan-400 text-xs px-2 py-1 rounded hover:bg-cyan-900/50 transition-colors"
        >
          VIEW FINGERPRINT
        </button>
      </div>

      {/* Fingerprint Modal */}
      {showFingerprint && fingerprint && (
        <div className="absolute inset-0 z-[2000] bg-slate-950/90 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-cyan-500 p-2 rounded max-w-full max-h-full relative">
            <button
              onClick={() => setShowFingerprint(false)}
              className="absolute top-2 right-2 text-white bg-red-500/50 hover:bg-red-500 rounded-full w-6 h-6 flex items-center justify-center"
            >
              &times;
            </button>
            <img src={`data:image/png;base64,${fingerprint}`} alt="Orbital Fingerprint" className="max-h-[300px] w-auto" />
            <div className="text-center text-cyan-400 text-xs mt-2">ORBITAL CLASSIFICATION MAP</div>
          </div>
        </div>
      )}
    </div>
  );
}