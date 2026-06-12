# 🚨 CRITICAL DEBUGGING CONTEXT: 3D Cesium Globe

**Current Status:**
The 3D Globe component (`SatelliteGlobe.js`) renders as a "Blue Ball" (default untextured sphere). No satellites, no terrain, no debug entities (Red Box) are visible. The FPS counter is also missing, suggesting the standard render loop might be stalled or hidden.

---

## A. System Architecture & Data Flow

### 1. The Stack
*   **Frontend:** Next.js (React 18), utilizing `resium` (React wrapper for CesiumJS).
*   **Backend:** Python `FastAPI` (Core API), reading from `Redis` Pub/Sub.
*   **Deployment:** Docker Compose. The `dashboard` service mounts local source code: `- ./services/dashboard:/app`.
*   **Asset Hosting:** Local files at `public/cesium/Assets/...`. Served by Next.js static file handler.

### 2. The Data Pipeline
1.  **`space-tracker` (Python):** Fetches TLEs from Space-Track.org, pushes `TLE_UPDATE` events to Redis.
2.  **`core-api` (Python):** Consumes Redis, broadcasts via WebSocket (`/ws/dashboard`).
3.  **Dashboard (`space.js`):** Receives WebSocket `TLE_UPDATE`.
4.  **`SatelliteGlobe.js`:**
    *   **Prop:** Receives `satellites` array (Objects containing TLE strings).
    *   **Logic:** Uses `satellite.js` to propagate TLE -> Lat/Long/Alt (Client-side).
    *   **Render:** Adds `PointPrimitive`s to the Cesium Scene.

---

## B. The Problem & Attempted Solutions

### The Symptoms
1.  **The "Blue Ball":** Globe appears as a solid blue sphere. No imagery (Bing, OSM, or Local) loads.
2.  **Invisible Satellites:** Even when data is verified flowing, no points appear.
3.  **Missing Debug UI:** Even when `debugShowFramesPerSecond={true}` is set, the FPS counter is not visible.

### Chronology of Fixes (What We Have Tried)

#### 1. Asset & Imagery Fixes (The "Blue Ball")
*   **Hypothesis:** Cesium cannot find the texture files (404 errors).
*   **Attempt 1:** Standard `Cesium.Ion` and `ArcGis` providers. (Result: Failed, likely network/key issues).
*   **Attempt 2:** Local `TileMapServiceImageryProvider`.
    *   *Action:* Verified `services/dashboard/public/cesium/Assets/Textures/NaturalEarthII/tilemapresource.xml` exists on disk.
    *   *Action:* Configured `CESIUM_BASE_URL` in `next.config.js`, `_app.js`, and finally `_document.js` (Global window var) to ensure correct base path `/cesium`.
    *   *Result:* Still Blue Ball.
*   **Attempt 3:** `SingleTileImageryProvider` (Moon/Earth JPG).
    *   *Result:* Still Blue Ball.
*   **Attempt 4 (Current):** `GridImageryProvider`.
    *   *Rationale:* Requires ZERO assets. Should draw coordinate lines.
    *   *Result:* User Reports "All I see is screenshot.png" (Static image?) or still Blue Ball.

#### 2. Rendering & Logic Fixes (Invisible Satellites)
*   **Hypothesis:** `Viewer` is not rendering new frames or Prop Logic is broken.
*   **Discovery:** Backend was sending TLEs, but Frontend expected pre-calculated `geo_lat`/`geo_lng`.
    *   *Fix:* Implemented Client-Side Orbit Propagation using `satellite.js` inside the `SatelliteGlobe` render loop.
*   **Discovery:** `GlobeManager` might be using a stale reference to a destroyed Scene.
    *   *Fix:* Rewrote `useEffect` to explicitly recreate `PointPrimitiveCollection` on every mount and cleanup on unmount.
*   **Hypothesis:** WebGL Crash.
    *   *Action:* Removed `Bloom` post-processing.
    *   *Action:* Removed `requestRenderMode` (forced standard render loop).

#### 3. Environment & Docker Fixes
*   **Issue:** "Slow Internet" causing Docker build timeouts (`ReadTimeoutError`).
    *   *Fix:* Patched ALL 23 Dockerfiles with `pip install --default-timeout=1000`.
*   **Issue:** Container exiting immediately.
    *   *Fix:* Created `test_space.sh` to run only relevant services.
    *   *Fix:* Removed "Aggressive Cleanup" (`docker prune`) from script to allow caching layers between failed runs.

---

## Current State Configuration
*   **`SatelliteGlobe.js`:**
    *   Imagery: `GridImageryProvider` (No assets required).
    *   Debug: `debugShowFramesPerSecond={true}`.
    *   Overlay: HTML `<div>` "DEBUG MODE ACTIVE".
*   **`_document.js`:**
    *   Sets `window.CESIUM_BASE_URL = '/cesium'` in `<Head>`.

**Request for Help:**
If the user sees a "Blue Ball" even with `GridImageryProvider`, and NO FPS counter, what is the most likely cause? Is Next.js failing to hydrate the Cesium component entirely? Is the Docker container missing GPU access (`/dev/dri`)?
