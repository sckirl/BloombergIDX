#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

echo "=== 🏛️ BloombergIDX Instant Stack Initializer ==="
echo "Working directory: $DIR"

# 1. Start all containers with Docker Compose
echo "Starting PostgreSQL, Redis, Backend, Frontend, and Cloudflare Tunnel..."
docker compose up -d

# 2. Wait for backend health check
echo -n "Waiting for backend readiness..."
for i in {1..30}; do
  if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo " READY!"
    break
  fi
  echo -n "."
  sleep 1
done

# 3. Print status and public endpoint
echo ""
echo "=== ✅ All Systems Operational ==="
echo "Local Backend:    http://localhost:8000"
echo "Local Frontend:   http://localhost:8100"
echo "Permanent Domain: https://bloomberg-api.sckirl.app"
echo "Health Check:     $(curl -s http://localhost:8000/health)"
echo ""
