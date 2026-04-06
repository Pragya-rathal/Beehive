import bcrypt
import pytest


@pytest.fixture
def created_user(mock_db):
    """Fixture to create a user in the mock database."""
    password = "securepassword"
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": hashed_pw,
    }
    mock_db.users.insert_one(user_data)
    return {"email": user_data["email"], "username": user_data["username"], "password": password}


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

def test_login_user_without_password(client, mock_db):
    """Test login for a user who exists but has no password set (e.g. OAuth user)."""
    mock_db.users.insert_one({
        "email": "oauth_user@example.com",
        "username": "oauthuser",
        "password": None
    })
    response = client.post(
        "/api/auth/login",
        json={"username": "oauth_user@example.com", "password": "somepassword"},
    )
    assert response.status_code == 401
    data = response.get_json()
    assert data == {"error": "Invalid credentials"}
