def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_and_list_points(client):
    response = client.post(
        "/auth/register",
        json={"email": "test@test.com", "password": "motdepasse123"}
    )
    assert response.status_code == 200

    login_response = client.post(
        "/auth/login",
        data={"username": "test@test.com", "password": "motdepasse123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    create_response = client.post(
        "/points",
        json={
            "name": "Tour Eiffel",
            "category": "monument",
            "latitude": 48.8584,
            "longitude": 2.2945
        },
        headers=headers
    )
    assert create_response.status_code == 200
    created_point = create_response.json()
    assert created_point["name"] == "Tour Eiffel"
    assert created_point["id"] is not None

    list_response = client.get("/points")
    assert list_response.status_code == 200
    points = list_response.json()
    assert len(points) == 1
    assert points[0]["name"] == "Tour Eiffel"

def test_create_point_requires_auth(client):
    response = client.post(
        "/points",
        json={
            "name": "Point non autorisé",
            "category": "test",
            "latitude": 48.8584,
            "longitude": 2.2945
        }
    )
    assert response.status_code == 401


def test_get_nonexistent_point_returns_404(client):
    response = client.get("/points/9999")
    assert response.status_code == 404