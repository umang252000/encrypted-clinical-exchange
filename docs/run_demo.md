# Run demo (local Codespace)

1. Build & run containers
   - open terminal at `infra/`
   - run: `docker compose up --build`

2. Ingest sample data (Hospital A)
   - POST single case:
     ```
     curl -X POST "http://localhost:8101/ingest_case" -H "Content-Type: application/json" -d '{"id":"A-1","text":"Elderly patient with chest pain","metadata":{"age":72}}'
     ```
   - Or upload CSV:
     ```
     curl -X POST "http://localhost:8101/ingest_csv" -F "file=@../examples/sample_cases.csv"
     ```

3. List encrypted blobs (proxy)
     curl http://localhost:8000/list_blobs


4. Clinician UI
- Open http://localhost:3000
- Upload hospital key file from `hospital-agent/hospital_a/keys/hospital_a.key` (present on host because we mounted keys volume).
- Click `List Encrypted Blobs` and `Decrypt locally`.

Notes:
- Keys are generated on first hospital container start if not present.
- The proxy stores only encrypted blobs under `cyborg-proxy/data`.
- Do not commit keys to Git. Treat produced `.key` files as secrets.