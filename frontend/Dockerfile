# Build stage
FROM node:18 as builder

WORKDIR /app
COPY . .

# Install and build the frontend
RUN npm install
RUN npm run build

# Production server stage
FROM nginx:alpine

# Copy built files to nginx default public folder
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80 for the frontend
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

