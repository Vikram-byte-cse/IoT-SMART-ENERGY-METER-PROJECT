# IoT Smart Energy Meter — cloud integration package

## What this package now includes

- Updated `Main Code.ino`: retains the existing ESP32 local access point/dashboard, sensor calculations, LCD and relay logic, and adds router Wi-Fi (AP+STA) plus HTTPS telemetry publishing every 10 seconds.
- `secrets.h.example`: private configuration template for Wi-Fi, API URL, device key and the API host root CA certificate.
- `main.py`: FastAPI backend with SQLite reading storage, protected ESP32 uploads, latest-reading and history endpoints.
- `index.html`: public read-only dashboard using the same dashboard design, reading from the cloud API.
- `api-config.js`: public API base URL setting for GitHub Pages.
- `Dockerfile`, `requirements.txt`, and `DEPLOYMENT_CHECKLIST.md`: portable backend deployment files and steps.

## Important: this is integration-ready, not already cloud-deployed

The firmware now contains the cloud publishing logic, but it cannot send readings until you deploy the API and fill in `secrets.h` with your own Wi-Fi credentials, device key, API URL, and valid TLS root CA certificate. The API URL and certificate depend on the backend host you choose. No hosting account or cloud database is created by this ZIP.

## Quick start

1. Read `DEPLOYMENT_CHECKLIST.md` and deploy FastAPI on a Python/Docker host (not Render or Netlify).
2. Configure a persistent volume for SQLite using `DATABASE_PATH`; without a persistent volume, cloud readings may be lost on restart/redeploy.
3. Set `DEVICE_API_KEY` and `CORS_ORIGINS` in the backend environment.
4. Put the backend base URL in `api-config.js`, then publish the static files to your GitHub Pages repository root.
5. Copy `secrets.h.example` to `secrets.h`, fill in the private values and valid root CA certificate, then compile/upload `Main Code.ino` to the ESP32.
6. Verify `/health`, `/api/readings/latest`, and the public website. See the checklist for exact tests.

## Local backend test (Windows PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
New-Item -ItemType Directory -Force data
$env:DEVICE_API_KEY = "use-a-long-random-secret"
$env:DATABASE_PATH = "./data/smart_meter.db"
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/health` and `http://127.0.0.1:8000/docs`.

## Hardware notes

The supplied firmware's calibration constants and measurements are not independently validated. Verify the exact ESP32 board, sensor modules, relay wiring and LCD before uploading. Do not connect mains circuits without properly rated isolation and qualified supervision. Cloud relay control is intentionally not implemented; the public dashboard only displays relay state.
