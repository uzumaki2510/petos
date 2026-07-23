FROM node:24.18-alpine
WORKDIR /app
COPY package.json pnpm-workspace.yaml ./
COPY apps/web/package.json ./apps/web/
RUN npm install -g pnpm && pnpm config set ignore-scripts false && pnpm install --filter web
COPY . .
WORKDIR /app/apps/web
# We use dev mode since this is a local development compose setup
CMD ["pnpm", "dev"]
