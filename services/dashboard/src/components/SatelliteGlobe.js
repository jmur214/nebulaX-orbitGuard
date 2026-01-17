import React, { useEffect, useRef } from 'react';
import { Viewer, Entity, useCesium, ScreenSpaceEventHandler, ScreenSpaceEvent } from 'resium';
import * as Cesium from 'cesium';

/**
 * Setup - Adds OSM imagery and configures initial camera
 */
const Setup = () => {
    const { viewer } = useCesium();
    const done = useRef(false);

    useEffect(() => {
        if (!viewer || done.current) return;
        done.current = true;

        console.log(">>> Setup: Configuring viewer");

        // Remove default imagery and add OSM
        while (viewer.imageryLayers.length > 0) {
            viewer.imageryLayers.remove(viewer.imageryLayers.get(0));
        }
        viewer.imageryLayers.addImageryProvider(
            new Cesium.OpenStreetMapImageryProvider({
                url: 'https://tile.openstreetmap.org/'
            })
        );
        console.log(">>> OSM added");

        // Set a nice initial camera view
        viewer.camera.setView({
            destination: Cesium.Cartesian3.fromDegrees(-95, 35, 20000000),
            orientation: {
                heading: Cesium.Math.toRadians(0),
                pitch: Cesium.Math.toRadians(-90),
                roll: 0
            }
        });
        console.log(">>> Camera positioned");
    }, [viewer]);

    return null;
};

/**
 * ClickHandler - Handles clicks on satellite entities
 */
const ClickHandler = ({ satellites, onSatelliteSelect }) => {
    const { viewer } = useCesium();

    useEffect(() => {
        if (!viewer || !onSatelliteSelect) return;

        // Set up click handler
        const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);

        handler.setInputAction((click) => {
            const pickedObject = viewer.scene.pick(click.position);

            if (Cesium.defined(pickedObject) && pickedObject.id) {
                const entity = pickedObject.id;
                const satName = entity.name;

                // Find matching satellite in data
                const sat = satellites.find(s => s.sat_name === satName);
                if (sat) {
                    console.log(">>> Clicked satellite:", satName);
                    onSatelliteSelect(sat);
                }
            }
        }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

        return () => {
            handler.destroy();
        };
    }, [viewer, satellites, onSatelliteSelect]);

    return null;
};

/**
 * SatelliteGlobe - Main globe component with satellite entities
 */
const SatelliteGlobe = ({ satellites = [], selectedSat, onSatelliteSelect }) => {
    useEffect(() => {
        console.log("=== SatelliteGlobe mounted, satellites:", satellites.length);
        if (satellites.length > 0) {
            console.log(">>> First satellite data:", satellites[0]);
            const withGeo = satellites.filter(s => s.geo_lat != null && s.geo_lng != null);
            console.log(">>> Satellites with geo coordinates:", withGeo.length, "/", satellites.length);
        }
    }, [satellites.length]);

    return (
        <div style={{ width: '100%', height: '100%' }}>
            <Viewer
                full
                timeline={false}
                animation={false}
                baseLayerPicker={false}
                geocoder={false}
                homeButton={true}
                sceneModePicker={false}
                navigationHelpButton={false}
                infoBox={true}
                selectionIndicator={true}
                imageryProvider={false}
            >
                <Setup />
                <ClickHandler satellites={satellites} onSatelliteSelect={onSatelliteSelect} />

                {/* Satellite entities */}
                {satellites.map((sat, index) => {
                    const lat = sat.geo_lat;
                    const lng = sat.geo_lng;
                    if (lat == null || lng == null) return null;

                    const isSelected = selectedSat?.sat_name === sat.sat_name;

                    return (
                        <Entity
                            key={sat.sat_name || index}
                            name={sat.sat_name}
                            description={`
                                <b>Satellite:</b> ${sat.sat_name}<br/>
                                <b>Altitude:</b> ${sat.geo_alt?.toFixed(1) || 'N/A'} km<br/>
                                <b>Latitude:</b> ${lat?.toFixed(3)}°<br/>
                                <b>Longitude:</b> ${lng?.toFixed(3)}°<br/>
                                <b>NORAD ID:</b> ${sat.norad_id || 'N/A'}
                            `}
                            position={Cesium.Cartesian3.fromDegrees(lng, lat, (sat.geo_alt || 400) * 1000)}
                            point={{
                                pixelSize: isSelected ? 18 : 10,
                                color: isSelected ? Cesium.Color.YELLOW : Cesium.Color.CYAN,
                                outlineColor: isSelected ? Cesium.Color.WHITE : Cesium.Color.TRANSPARENT,
                                outlineWidth: isSelected ? 2 : 0
                            }}
                        />
                    );
                })}
            </Viewer>

            {/* Info overlay */}
            <div style={{
                position: 'absolute',
                bottom: 20,
                left: 20,
                background: 'rgba(10, 20, 40, 0.9)',
                padding: '12px 16px',
                borderRadius: '8px',
                color: 'white',
                zIndex: 1000,
                pointerEvents: 'none'
            }}>
                <div style={{ fontWeight: 'bold', marginBottom: '4px', color: '#60a5fa' }}>ORBIT GUARD</div>
                <div>Satellites: <span style={{ color: '#10b981' }}>{satellites.length}</span></div>
                {selectedSat && (
                    <div style={{ marginTop: '4px', borderTop: '1px solid #4a5568', paddingTop: '4px' }}>
                        Selected: <span style={{ color: '#fbbf24' }}>{selectedSat.sat_name}</span>
                    </div>
                )}
            </div>

            {/* Instructions */}
            <div style={{
                position: 'absolute',
                top: 10,
                right: 10,
                background: 'rgba(10, 20, 40, 0.8)',
                padding: '8px 12px',
                borderRadius: '4px',
                color: '#9ca3af',
                fontSize: '12px',
                zIndex: 1000,
                pointerEvents: 'none'
            }}>
                Click satellite to select • Scroll to zoom
            </div>
        </div>
    );
};

export default SatelliteGlobe;
