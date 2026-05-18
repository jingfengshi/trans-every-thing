FROM node:20-slim

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --ignore-scripts 2>/dev/null || npm install

COPY . .

CMD ["npm", "run", "dev"]
