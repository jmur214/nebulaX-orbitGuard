import React, { useEffect, useRef } from 'react';
import { Viewer, Entity, useCesium, ScreenSpaceEventHandler, ScreenSpaceEvent } from 'resium';
import * as Cesium from 'cesium';

// Country-to-Color mapping for satellite visualization
const COUNTRY_COLORS = {
    'US': Cesium.Color.fromCssColorString('#3B82F6'),      // Blue (USA)
    'CIS': Cesium.Color.fromCssColorString('#EF4444'),     // Red (Russia/CIS)
    'RUS': Cesium.Color.fromCssColorString('#EF4444'),     // Red (Russia)
    'PRC': Cesium.Color.fromCssColorString('#F59E0B'),     // Orange (China)
    'CHN': Cesium.Color.fromCssColorString('#F59E0B'),     // Orange (China alternate code)
    'ESA': Cesium.Color.fromCssColorString('#8B5CF6'),     // Purple (European Space Agency)
    'JPN': Cesium.Color.fromCssColorString('#EC4899'),     // Pink (Japan)
    'IND': Cesium.Color.fromCssColorString('#10B981'),     // Emerald (India)
    'FR': Cesium.Color.fromCssColorString('#6366F1'),      // Indigo (France)
    'UK': Cesium.Color.fromCssColorString('#14B8A6'),      // Teal (UK)
    'GER': Cesium.Color.fromCssColorString('#84CC16'),     // Lime (Germany)
    'CA': Cesium.Color.fromCssColorString('#F97316'),      // Orange-red (Canada)
    'ISR': Cesium.Color.fromCssColorString('#06B6D4'),     // Cyan (Israel)
    'UNK': Cesium.Color.fromCssColorString('#6B7280'),     // Gray (Unknown)
};

// Helper function to get color for a satellite
const getSatelliteColor = (sat, isSelected) => {
    if (isSelected) return Cesium.Color.YELLOW;

    const country = sat.verified_metadata?.country || sat.origin_prediction?.country || 'UNK';
    return COUNTRY_COLORS[country] || COUNTRY_COLORS['UNK'];
};

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

        // Use Cesium's default Ion-backed imagery (Bing). The Ion token is set
        // in _app.js. Don't override with raw OpenStreetMap tiles — OSM's tile
        // usage policy blocks shared-infra hosts (Codespaces *.app.github.dev,
        // many cloud IPs) which manifests as "blocked by usage policy".

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
const SatelliteGlobe = ({ satellites = [], selectedSat, orbitPath, onSatelliteSelect }) => {
    useEffect(() => {
        console.log("=== SatelliteGlobe mounted, satellites:", satellites.length);
        if (satellites.length > 0) {
            console.log(">>> First satellite data:", satellites[0]);
            const withGeo = satellites.filter(s => s.geo_lat != null && s.geo_lng != null);
            console.log(">>> Satellites with geo coordinates:", withGeo.length, "/", satellites.length);
            console.log(">>> Satellites with geo coordinates:", withGeo.length, "/", satellites.length);
        }
    }, [satellites.length]);

    // DEBUG: Log Orbit Path updates
    useEffect(() => {
        if (orbitPath && orbitPath.length > 0) {
            console.log(">>> SatelliteGlobe received orbitPath points:", orbitPath.length);
            console.log(">>> First point:", orbitPath[0]); // [lat, lon, alt]
        } else {
            console.log(">>> SatelliteGlobe orbitPath is NULL");
        }
    }, [orbitPath]);

    // Convert orbitPath prop to Cesium format - use useMemo to ensure proper updates
    const orbitPositions = React.useMemo(() => {
        if (!orbitPath || orbitPath.length === 0) return null;

        const flatArray = [];
        orbitPath.forEach(point => {
            // API returns [lat, lon, alt_km]
            flatArray.push(point[1]); // longitude
            flatArray.push(point[0]); // latitude
            flatArray.push((point[2] || 400) * 1000); // altitude in meters
        });

        console.log(">>> Computing orbitPositions, first coords: lon=" + flatArray[0] + ", lat=" + flatArray[1]);
        return Cesium.Cartesian3.fromDegreesArrayHeights(flatArray);
    }, [orbitPath]);

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

                {/* Orbit Path - single entity for selected satellite */}
                {selectedSat && orbitPositions && (
                    <Entity
                        key={`orbit-${selectedSat.sat_name}`} // Force re-mount on change
                        polyline={{
                            positions: orbitPositions,
                            width: 3,
                            material: Cesium.Color.CYAN.withAlpha(0.8),
                            clampToGround: false
                        }}
                    />
                )}

                {/* Satellite entities */}
                {satellites.map((sat, index) => {
                    const lat = sat.geo_lat;
                    const lng = sat.geo_lng;
                    if (lat == null || lng == null) return null;

                    const isSelected = selectedSat?.sat_name === sat.sat_name;
                    const country = sat.verified_metadata?.country || sat.origin_prediction?.country || 'UNK';
                    const satColor = getSatelliteColor(sat, isSelected);

                    return (
                        <Entity
                            key={sat.sat_name || index}
                            name={sat.sat_name}
                            description={`
                                <b>Satellite:</b> ${sat.sat_name}<br/>
                                <b>Country:</b> ${country}<br/>
                                <b>Altitude:</b> ${sat.geo_alt?.toFixed(1) || 'N/A'} km<br/>
                                <b>Latitude:</b> ${lat?.toFixed(3)}°<br/>
                                <b>Longitude:</b> ${lng?.toFixed(3)}°<br/>
                                <b>NORAD ID:</b> ${sat.norad_id || 'N/A'}
                            `}
                            position={Cesium.Cartesian3.fromDegrees(lng, lat, (sat.geo_alt || 400) * 1000)}
                            point={{
                                pixelSize: isSelected ? 18 : 12,
                                color: satColor,
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
