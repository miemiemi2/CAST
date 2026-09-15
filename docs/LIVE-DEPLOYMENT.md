# Public live app

URL: https://luluhu.com/cast/

The public app runs the existing browser and Python runtimes through `cast.public:app`. It seeds a small PLAYER / CARGO / GOAL prototype with a generic proximity-based attachment. Designer requests are sent to the real Strands gateway; there is no model fallback.

Each visitor receives a random Secure / HttpOnly / SameSite session cookie and a separate durable scene, ruleset, recordings and audit log. Session state survives application restarts. The public route excludes camera, signal and scene administration endpoints. Model calls are serialized: eight intent requests per session, twenty per IP per hour, and a separate durable gateway cap of 100 model requests per UTC day (each intent can use up to three model requests). Pointer input and replay do not invoke the model.

Deployment uses the existing VPS and HTTPS reverse proxy, with separate systemd services `cast-live` and `cast-live-gateway`. The gateway listens only on loopback. The public app listens on the private Docker bridge. Neither service depends on the Mac remaining online.

To run behind an HTTPS proxy at `/cast/`:

```sh
CAST_AGENT_URL=http://127.0.0.1:18877 \
CAST_PUBLIC_DATA=/var/lib/cast-live/sessions \
.venv/bin/uvicorn cast.public:app --host 127.0.0.1 --port 18766 --workers 1
```

The reverse proxy preserves the `/cast/` prefix, sets `Host` and overwrites `X-Real-IP`, permits a 1 MB body, and allows 150 seconds for model responses. Use exactly one application worker because the model lock is process-local. Keep the model gateway private and configure its ADC separately.

Validation: a real browser visited the HTTPS URL, recorded pointer input, requested a slow-only acquisition rule through Strands/Vertex, replayed identical input/snapshot under both versions, tried and kept the candidate. OLD Cargo finished at x≈0.963; NEW stayed at x=0.48. A second browser session retained its original revision. Evidence is in `records/public-live/`. The standalone isolation smoke check runs without a provider call:

```sh
.venv/bin/python -m scripts.public_smoke
```
