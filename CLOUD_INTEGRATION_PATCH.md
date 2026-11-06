# Cloud integration status

The cloud publishing changes have now been added directly to `Main Code.ino` in this package. Do not apply the older snippets from previous versions of this document.

Follow `DEPLOYMENT_CHECKLIST.md` instead. In particular:

- Deploy the FastAPI backend first.
- Configure `DEVICE_API_KEY`, `CORS_ORIGINS`, and a persistent `DATABASE_PATH` on the backend host.
- Copy `secrets.h.example` to `secrets.h` and fill in your own 2.4 GHz Wi-Fi credentials, HTTPS `/api/readings` URL, matching device key, and valid root CA certificate.
- Compile and upload the updated firmware only after `secrets.h` has been created and the certificate placeholder replaced.

The firmware retains the local ESP32 dashboard and adds HTTPS telemetry publishing. The public dashboard is read-only; cloud relay control is not implemented.
