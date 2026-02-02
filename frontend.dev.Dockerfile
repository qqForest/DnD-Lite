FROM node:20-slim

WORKDIR /frontend

# Install dependencies first (for better caching)
COPY frontend/package*.json ./
RUN npm install

# Copy source code
COPY frontend/ .

EXPOSE 3000

# Run vite dev server, expose to 0.0.0.0 for docker access
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
