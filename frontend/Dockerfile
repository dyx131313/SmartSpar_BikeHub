# Build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY frontend/bikehub/package*.json ./
RUN npm ci --silent
COPY frontend/bikehub/ ./
RUN npm run build

# Production stage: serve with nginx
FROM nginx:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html
# Copy optional nginx config if provided
COPY deploy/nginx/conf.d/ /etc/nginx/conf.d/
