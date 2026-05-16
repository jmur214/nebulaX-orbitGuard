# Production-style multi-stage build for the NebulaX dashboard.
# - Default for `docker compose up`: smaller image, faster startup, no hot reload.
# - For hot reload in Docker, use Dockerfile.dev via docker-compose.dev.yml:
#     docker compose -f docker-compose.yml -f docker-compose.dev.yml up
# - For fastest iteration, run dashboard on the host: ./dev.sh

# ---------- Stage 1: deps ----------
FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --no-audit --no-fund

# ---------- Stage 2: builder ----------
FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Cesium ships its runtime assets in node_modules; copy them into /public for serving.
RUN mkdir -p public/cesium && cp -r node_modules/cesium/Build/Cesium/* public/cesium/
RUN npm run build

# ---------- Stage 3: runtime ----------
FROM node:18-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/next.config.js ./next.config.js
EXPOSE 3000
CMD ["npm", "run", "start"]
