#!/bin/bash
set -e

echo "🔐 Generating tokens..."

ADMIN_TOKEN=$(python3 auth/generate_jwt.py --sub hospital-agent --role admin)
CLINICIAN_TOKEN=$(python3 auth/generate_jwt.py --sub alice --role clinician)

export ADMIN_TOKEN
export CLINICIAN_TOKEN

echo "🚀 Starting containers..."
cd infra
docker compose down
docker compose up --build -d
cd ..

sleep 10

echo "🏥 Ingesting hospital data..."
curl -X POST http://localhost:8101/ingest_example
curl -X POST http://localhost:8201/ingest_example

echo "🧪 Running auth tests..."
pytest tests/integration

echo "🌐 Open UI: http://localhost:3000"
echo "👩‍⚕️ Clinician token:"
echo "$CLINICIAN_TOKEN"