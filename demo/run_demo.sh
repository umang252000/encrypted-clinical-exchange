#!/bin/bash
set -e

echo "🚀 Starting full encrypted clinical demo..."

(cd infra && docker compose up --build -d)

echo "⏳ Waiting for services..."
sleep 10

echo "🔐 Generating clinician token..."
TOKEN=$(python3 auth/generate_jwt.py --sub demo-clinician --role clinician)
echo "TOKEN=$TOKEN"

echo "🏥 Ingesting example data (Hospital A + B)..."
curl -X POST http://localhost:8101/ingest_example
curl -X POST http://localhost:8201/ingest_example

echo "📦 Listing encrypted blobs..."
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/list_blobs

echo "🧪 Running privacy leakage experiment..."
python3 tests/privacy/embedding_leakage_test.py

echo "📜 Running audit analysis..."
python3 tools/audit_analyzer.py

echo "✅ DEMO COMPLETE — system verified end-to-end"