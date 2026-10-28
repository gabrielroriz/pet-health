# Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
fastapi dev
```

The API runs at http://localhost:8000 and the docs at http://localhost:8000/docs.

Settings are read from environment variables or a `.env` file (see `app/config.py`).

## Docker

From the repository root:

```bash
docker compose up --build
```

Uvicorn serves the API at http://localhost:8000 and reloads when files in `app/` change. Set `BACKEND_PORT` to use another host port (`BACKEND_PORT=8001 docker compose up`). Rebuild after changing `requirements.txt`.

## Tests

```bash
pytest
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the internal structure.
