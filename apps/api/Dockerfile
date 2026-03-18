FROM node:20-alpine

WORKDIR /app

# Install dependencies first (better cache)
COPY package.json package-lock.json ./
RUN npm ci

# Copy source (dev compose will bind-mount over /app, but keep node_modules volume)
COPY . .

EXPOSE 4000

CMD ["npm", "run", "dev"]

