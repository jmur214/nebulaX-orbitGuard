import React, { useEffect, useRef } from 'react';
import Globe from 'globe.gl';

export default function SatelliteGlobe({ telemetry }) {
  const globeContainer = useRef();
  const globeInstance = useRef();

  useEffect(() => {
    // Initialize Globe
    if (globeContainer.current && !globeInstance.current) {
      globeInstance.current = Globe()(globeContainer.current)
        .width(400)
        .height(400)
        .backgroundColor('rgba(0,0,0,0)')
        .globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg')
        .backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png')
        .pointRadius(0.5)
        .pointAltitude(0)
        .pointColor('color');
      
      // Auto-rotate
      globeInstance.current.controls().autoRotate = true;
      globeInstance.current.controls().autoRotateSpeed = 0.5;
    }
  }, []);

  useEffect(() => {
    if (globeInstance.current) {
      // Update Satellite Data
      const satData = telemetry ? [{
        lat: telemetry.geo_lat,
        lng: telemetry.geo_lng,
        alt: telemetry.geo_alt / 6371,
        name: telemetry.sat_name,
        color: telemetry.visibility === 'VISIBLE' ? '#ef4444' : '#06b6d4'
      }] : [];

      const stationData = [{
        lat: 37.7749,
        lng: -122.4194,
        name: "HOME BASE",
        color: "#10b981"
      }];

      // Combine data for rendering
      // We use 'objects' layer for satellite and 'points' for ground station
      globeInstance.current
        .objectsData(satData)
        .objectLat('lat')
        .objectLng('lng')
        .objectAltitude('alt')
        .objectLabel('name')
        .objectColor('color')
        .pointsData(stationData);
    }
  }, [telemetry]);

  return (
    <div className="flex justify-center items-center overflow-hidden rounded-sm border border-cyan-900/50 bg-slate-900/50 relative">
      <div ref={globeContainer} />
      <div className="absolute bottom-2 right-2 text-[10px] text-cyan-700 font-mono tracking-widest">
        LIVE ORBITAL VIEW
      </div>
    </div>
  );
}