FROM node:22-alpine AS web-build
WORKDIR /build/web-react
COPY web-react/package.json web-react/package-lock.json ./
RUN npm ci
COPY web-react/ ./
ARG VITE_API_URL=""
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8003
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY server/ server/
COPY ml/ ml/
COPY models/best_cervical.pt models/best_cervical.pt
COPY --from=web-build /build/web-dist web-dist/
RUN mkdir -p artifacts
EXPOSE 8003
CMD ["sh", "-c", "uvicorn server.app:app --host 0.0.0.0 --port ${PORT}"]
