FROM node:18-alpine

WORKDIR /app

# 1. Install Dependencies from package.json
COPY package*.json ./
RUN npm install

# 2. Copy code
COPY . .

# 3. Setup Cesium Assets
RUN mkdir -p public/cesium && cp -r node_modules/cesium/Build/Cesium/* public/cesium/

# 4. Pre-build for faster startup (optional - comment out for dev mode)
# RUN npm run build

# 5. Start (use dev for hot reload, start for production)
CMD ["npm", "run", "dev"]