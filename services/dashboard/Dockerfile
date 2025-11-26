FROM node:18-alpine

WORKDIR /app

# 1. FORCE CLEAN INSTALL
# We explicitly pin tailwindcss@3.4.1 to avoid the v4.0 breaking changes
RUN npm install next@14.0.4 \
                react@18.2.0 \
                react-dom@18.2.0 \
                axios \
                date-fns \
                leaflet@1.9.4 \
                react-leaflet@4.2.1 \
                autoprefixer@10.4.16 \
                postcss@8.4.31 \
                tailwindcss@3.4.1

# 2. Copy code
COPY . .

# 3. Start
CMD ["npm", "run", "dev"]