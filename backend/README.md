# Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
fastapi dev app/main.py
```

The API runs at http://localhost:8000 and the docs at http://localhost:8000/docs.

Settings are read from environment variables or a `.env` file (see `app/config.py`).

## Tests

```bash
pytest
```
