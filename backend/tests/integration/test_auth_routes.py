from tests.integration.conftest import log_in


def test_login_returns_bearer_token(client):
    response = client.post("/auth/login", json={"email": "ana@example.com"})

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_rejects_invalid_email(client):
    assert client.post("/auth/login", json={"email": "not-an-email"}).status_code == 422


def test_me_returns_logged_in_user(client):
    response = client.get("/auth/me", headers=log_in(client, "Ana@Example.com"))

    assert response.status_code == 200
    assert response.json()["email"] == "ana@example.com"


def test_me_requires_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_me_rejects_unknown_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer unknown"})

    assert response.status_code == 401
