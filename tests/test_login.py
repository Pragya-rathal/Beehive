import bcrypt
import pytest


@pytest.fixture
def created_user(mock_db):
    """Fixture factory to create users in the mock database."""

    def _create_user(email="test@example.com", username="testuser", password="securepassword"):
        stored_password = None if password is None else bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        user_data = {"email": email, "username": username, "password": stored_password}
        mock_db.users.insert_one(user_data)
        return {"email": email, "username": username, "password": password}

    default_user = _create_user()

    class _UserFactory:
        def __call__(self, **kwargs):
            return _create_user(**kwargs)

        def __getitem__(self, key):
            return default_user[key]

    return _UserFactory()


@pytest.mark.parametrize("login_identifier_key", ["email", "username"])
def test_login_success(client, created_user, login_identifier_key):
    """
    POST /api/auth/login with valid credentials (email or username).
    """
    response = client.post(
        "/api/auth/login",
        json={
            "username": created_user[login_identifier_key],
            "password": created_user["password"],
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data


@pytest.mark.parametrize(
    "username,password",
    [("missing@example.com", "wrongpassword"), ("test@example.com", "wrongpassword")],
)
def test_login_invalid_credentials(client, created_user, username, password):
    """POST /api/auth/login - all authentication failures should return generic 401."""
    response = client.post("/api/auth/login", json={"username": username, "password": password})

    assert response.status_code == 401
    data = response.get_json()
    assert data == {"error": "Invalid credentials"}


def test_login_user_without_password(client, created_user):
    """POST /api/auth/login - users without local password should get generic 401."""
    oauth_user = created_user(email="oauth@example.com", username="oauthuser", password=None)

    response = client.post(
        "/api/auth/login",
        json={"username": oauth_user["email"], "password": "somepassword"},
    )

    assert response.status_code == 401
    assert response.get_json() == {"error": "Invalid credentials"}
