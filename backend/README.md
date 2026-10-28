# Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
fastapi dev
```

The API runs at http://localhost:8000 and the docs at http://localhost:8000/docs.

Settings are read from environment variables or a `.env` file (see `app/config.py`).

## Tests

```bash
pytest
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the internal structure.
