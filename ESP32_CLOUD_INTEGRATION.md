# ESP32 cloud connection

The updated `Main Code.ino` already includes the cloud telemetry code. Complete the host-specific setup in `DEPLOYMENT_CHECKLIST.md` before compiling it.

1. Deploy `main.py` and configure the API's `DEVICE_API_KEY` plus persistent `DATABASE_PATH`.
2. Set `api-config.js` to the deployed API base URL and publish the static dashboard through GitHub Pages.
3. Copy `secrets.h.example` to `secrets.h` beside `Main Code.ino`.
4. Set `ROUTER_SSID`, `ROUTER_PASSWORD`, `CLOUD_READINGS_URL` (full HTTPS URL ending in `/api/readings`), and the matching `DEVICE_API_KEY`.
5. Replace the root CA certificate placeholder with the valid certificate for the deployed API hostname. The code validates TLS; it does not disable certificate checks.
6. Compile and upload using Arduino IDE with the ESP32 board package and the libraries already required by the original sketch.
7. Open Serial Monitor at 115200 baud and check for successful `Cloud POST status` responses.

The ESP32 continues to provide its local access point at `192.168.4.1` while joining the configured 2.4 GHz router. Cloud uploads are telemetry-only. The public website does not control the relay.
