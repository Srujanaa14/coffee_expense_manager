def test_register_page_loads(client):
    res = client.get("/auth/register")
    assert res.status_code == 200

def test_login_page_loads(client):
    res = client.get("/auth/login")
    assert res.status_code == 200

def test_register_and_login(client):
    # Register
    res = client.post("/auth/register", data={
        "full_name":        "Test Farmer",
        "email":            "test@farm.com",
        "password":         "test123",
        "confirm_password": "test123",
    }, follow_redirects=True)
    assert res.status_code == 200

    # Login
    res = client.post("/auth/login", data={
        "email":    "test@farm.com",
        "password": "test123",
    }, follow_redirects=True)
    assert res.status_code == 200

def test_wrong_password(client):
    res = client.post("/auth/login", data={
        "email":    "test@farm.com",
        "password": "wrongpassword",
    }, follow_redirects=True)
    assert b"Invalid" in res.data