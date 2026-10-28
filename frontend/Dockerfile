FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json ./
RUN corepack enable && pnpm install --no-frozen-lockfile

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN corepack enable && pnpm build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup -S folio && adduser -S folio -G folio
COPY --from=builder /app/public ./public
COPY --from=builder --chown=folio:folio /app/.next/standalone ./
COPY --from=builder --chown=folio:folio /app/.next/static ./.next/static
USER folio
EXPOSE 3000
ENV PORT=3000 HOSTNAME=0.0.0.0
CMD ["node", "server.js"]
