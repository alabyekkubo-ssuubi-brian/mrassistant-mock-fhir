# Google Cloud Run Deployment

This document describes how to package and deploy the MCP HTTP server in `mcp-server/` to Google Cloud Run.

## Build the container image

From `mcp-server/`:

```bash
cd mcp-server
docker build -t gcr.io/<PROJECT_ID>/mrassistant-mcp-server:latest .
```

## Push the image to Google Container Registry

```bash
docker push gcr.io/<PROJECT_ID>/mrassistant-mcp-server:latest
```

## Cloud Run deploy command

Use `gcloud run deploy` with your own service name and settings:

```bash
gcloud run deploy mrassistant-backend \
  --image="gcr.io/<PROJECT_ID>/mrassistant-mcp-server:latest" \
  --region="us-central1" \
  --project="<PROJECT_ID>" \
  --platform=managed \
  --allow-unauthenticated \
  --port=8000 \
  --memory=2Gi \
  --cpu=2 \
  --timeout=3600 \
  --concurrency=10 \
  --min-instances=1 \
  --max-instances=10 \
  --env-vars-file=env.yaml
```

### Optional Cloud Run settings

If you need Cloud SQL or VPC access, add flags such as:

```bash
  --add-cloudsql-instances="<PROJECT_ID>:us-central1:<INSTANCE_NAME>" \
  --vpc-connector="<CONNECTOR_NAME>" \
  --vpc-egress=private-ranges-only
```

## Deploy HAPI FHIR to Cloud Run

The FHIR backend can also run as a separate Cloud Run service. This is a separate deployment from the MCP server.

```bash
gcloud run deploy mrassistant-fhir \
  --image="hapiproject/hapi:latest" \
  --region="us-central1" \
  --project="<PROJECT_ID>" \
  --platform=managed \
  --allow-unauthenticated \
  --port=8080 \
  --memory=2Gi \
  --cpu=1 \
  --timeout=3600 \
  --concurrency=10 \
  --min-instances=0 \
  --max-instances=5
```

After deployment, update the MCP service environment to point to the FHIR service URL.

For example, if FHIR is available at:

```text
https://mrassistant-fhir-xxxxxxxxxx-uc.a.run.app/fhir
```

then set `FHIR_BASE_URL` in `env.yaml` to that value before deploying the MCP service.

### Loading mock data into remote FHIR

The repository loader now supports `FHIR_BASE_URL` from the environment. Run from `mcp-server/`:

Using the Makefile (recommended):

```bash
make cloudrun-load-data FHIR_URL=https://mrassistant-fhir-xxxxxxxxxx-uc.a.run.app/fhir
```

Or directly:

```bash
FHIR_BASE_URL="https://mrassistant-fhir-xxxxxxxxxx-uc.a.run.app/fhir" uv run python scripts/load_mock_data.py
```

On Windows PowerShell:

```powershell
$env:FHIR_BASE_URL = "https://mrassistant-fhir-xxxxxxxxxx-uc.a.run.app/fhir"
uv run python scripts/load_mock_data.py
```

## Environment variables

The service requires the following environment variables:

- `FHIR_BASE_URL` — the URL to your FHIR server endpoint (for example, `https://<YOUR_FHIR_HOST>/fhir`).
- `TIMEZONE` — timezone used by slot and appointment helpers.
- `MCP_HTTP_PORT` — optional; Cloud Run also provides `PORT` automatically.

Copy `env.yaml.example` to `env.yaml` and update the values for your deployment.

## Notes

- Cloud Run supplies the `PORT` environment variable automatically; the server now supports `PORT` as well as `MCP_HTTP_PORT`.
- The service runs the HTTP MCP transport at `/mcp` and exposes health at `/health`.
- Ensure your FHIR backend is reachable from Cloud Run using the configured `FHIR_BASE_URL`.
