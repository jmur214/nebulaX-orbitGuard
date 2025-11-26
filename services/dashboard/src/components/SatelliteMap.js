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

export default function SatelliteMap({ telemetry }) {
  // SAFETY CHECK: Ensure we have actual coordinates.
  // Old database records might be missing these fields, which caused the crash.
  const hasGPS = telemetry &&
    typeof telemetry.geo_lat === 'number' &&
    typeof telemetry.geo_lng === 'number';

  // Default to [0,0] if data is missing/loading
  const center = hasGPS ? [telemetry.geo_lat, telemetry.geo_lng] : [0, 0];

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

        {/* Auto-center the map when satellite moves */}
        <MapController center={center} />

        {/* Satellite Marker (Only render if we have data) */}
        {hasGPS && (
          <>
            {/* Orbit Path Line */}
            {telemetry.orbit_path && (
              <React.Fragment>
                {/* We use a simple Polyline. Note: Crossing the dateline might look weird without splitting, 
                     but for a simple viz it's often acceptable or we can handle it later. */}
                <Polyline
                  positions={telemetry.orbit_path}
                  pathOptions={{ color: '#06b6d4', weight: 2, opacity: 0.5, dashArray: '5, 10' }}
                />
              </React.Fragment>
            )}

            {/* Sensor Footprint (Coverage Area) */}
            <Circle
              center={center}
              radius={2500000} // ~2500km radius for a weather satellite
              pathOptions={{ color: '#06b6d4', fillColor: '#06b6d4', fillOpacity: 0.1, weight: 1 }}
            />

            <Marker position={center} icon={satIcon}>
              <Popup>
                <div className="text-slate-900 font-bold">{telemetry.sat_name}</div>
                <div className="text-slate-600 text-xs">
                  Lat: {telemetry.geo_lat.toFixed(2)} <br />
                  Lng: {telemetry.geo_lng.toFixed(2)} <br />
                  Alt: {Math.round(telemetry.geo_alt || 0)} km
                </div>
              </Popup>
            </Marker>
          </>
        )}

        {/* Ground Station (Green Dot) */}
        <Marker position={[37.7749, -122.4194]} icon={L.divIcon({
          html: "<div style='background-color: #10b981; width: 10px; height: 10px; border-radius: 50%; box-shadow: 0 0 10px #10b981;'></div>",
          className: ''
        })}>
          <Popup>GROUND STATION ALPHA</Popup>
        </Marker>

      </MapContainer>
    </div>
  );
}