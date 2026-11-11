import os
os.environ.setdefault('DATA_ENCRYPTION_KEY','')
from app.security import hash_password, verify_password

def test_password_hash_roundtrip():
    hashed=hash_password('a-long-test-password-123')
    assert verify_password('a-long-test-password-123',hashed)
    assert not verify_password('wrong-password',hashed)
