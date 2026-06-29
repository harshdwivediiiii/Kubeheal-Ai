# ---- build stage ----
FROM node:24-alpine AS build

WORKDIR /app
COPY app/package.json .
RUN npm install --production

# ---- runtime stage ----
FROM node:24-alpine

WORKDIR /app
COPY --from=build /app/node_modules ./node_modules
COPY app/ .

ENV PORT=3000
EXPOSE 3000

# Run as non-root for security
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

CMD ["node", "index.js"]
