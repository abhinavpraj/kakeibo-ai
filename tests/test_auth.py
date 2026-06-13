from auth.auth import authenticate_user, create_user, hash_password, verify_password


def test_password_hashing():
    pwd = "mytestpassword"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_create_and_authenticate_user():
    # Test unique registration
    success, msg = create_user("testuser", "password123")
    assert success is True
    assert msg == "User registered successfully."

    # Test duplicate registration
    success, msg = create_user("testuser", "password123")
    assert success is False
    assert "already taken" in msg

    # Test authentication success
    success, msg, user_id = authenticate_user("testuser", "password123")
    assert success is True
    assert user_id is not None

    # Test authentication failure (wrong password)
    success, msg, user_id = authenticate_user("testuser", "wrongpassword")
    assert success is False
    assert user_id is None
