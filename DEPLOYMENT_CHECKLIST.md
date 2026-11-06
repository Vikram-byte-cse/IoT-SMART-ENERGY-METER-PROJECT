# Cloud deployment checklist (no Render / no Netlify)

This package is host-neutral. Use GitHub Pages for the static website and any Python-capable host for FastAPI. A Docker-capable host is easiest; use the included `Dockerfile` or deploy `main.py` with `requirements.txt`.

## Backend environment variables

Set these in the backend host's service settings:

- `DEVICE_API_KEY`: a long random secret (at least 32 random bytes). Keep it private.
- `CORS_ORIGINS`: your GitHub Pages origin only, e.g. `https://vikram-byte-cse.github.io` (no repository path).
- `DATABASE_PATH`: a file path on a persistent mounted volume, e.g. `/data/smart_meter.db`.
- `PORT`: supplied automatically by many hosts; otherwise use `8000`.

**Persistent storage is essential.** If the host's filesystem is ephemeral, SQLite data can disappear on redeploy/restart. Attach a persistent volume and set `DATABASE_PATH` to a file inside it. For multi-instance/high-volume deployment, use a managed PostgreSQL database and adapt the database layer before enabling multiple replicas.

## Deploy the API

1. Deploy this folder as a Docker service or Python web service using `requirements.txt`.
2. Attach persistent storage and configure the environment variables above.
3. Open `https://YOUR-API-HOST/health`; expect `status: ok`.
4. Open `https://YOUR-API-HOST/docs`; confirm the API documentation loads.
5. Keep `/api/readings` protected by `X-Device-Key`. Do not place this key in `index.html` or `api-config.js`.

## Configure the public site

Edit `api-config.js` and replace the placeholder with the backend base URL, without a trailing slash. Push `index.html` and `api-config.js` to the root of the GitHub Pages branch. The page polls `/api/readings/latest` and displays a disconnected/waiting state until the ESP32 posts a reading.

## Configure the ESP32

1. Copy `secrets.h.example` to `secrets.h` in the same folder as `Main Code.ino`.
2. Fill in the router's 2.4 GHz SSID/password, full HTTPS `/api/readings` URL, and the exact same `DEVICE_API_KEY` used on the backend.
3. Replace the certificate placeholder with the valid root CA chain required by the API host. The firmware uses `tls.setCACert()` and verifies the server certificate.
4. Keep `secrets.h` private; `.gitignore` excludes it.
5. Select the correct ESP32 board and COM port in Arduino IDE, then compile and upload. Check Serial Monitor at 115200 baud for `Cloud POST status: 200` or another 2xx status.

## Expected behavior

- The ESP32 keeps its existing local AP dashboard at `192.168.4.1` and also joins the configured 2.4 GHz router in AP+STA mode.
- Telemetry is posted every 10 seconds while the router connection is available.
- If Wi-Fi/cloud is unavailable, the local AP/dashboard continues; cloud data is not uploaded until connectivity returns.
- The public website is read-only. Relay control is not exposed by the cloud API.

## Verification

1. `GET /health` returns `status: ok`.
2. Before the first device post, `GET /api/readings/latest` reports `connected: false`.
3. After a successful ESP32 POST, `GET /api/readings/latest` returns the latest values and `connected: true` while the device has posted within 30 seconds.
4. `GET /api/readings/history?limit=20` returns stored samples.

## Security and safety

- Never commit `secrets.h`, Wi-Fi passwords, or device keys.
- Do not add remote relay control to this API. The existing ESP32 `/relay` route is local and unauthenticated.
- Use properly isolated, correctly rated sensors/relay hardware and qualified supervision for any mains-connected testing. This project is not a certified billing meter or safety controller.
- Calibrate and validate measurements against reference instruments before relying on them.
