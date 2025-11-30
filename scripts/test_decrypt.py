# test_decrypt_token.py - Run this to decrypt and check token
from app.core.database import SessionLocal
from app.models.oauth_models import UserEmailToken
from app.utils.encryption import decrypt_field, EncryptionKeys

db = SessionLocal()
try:
    token_id = 2  # Change to new token ID after re-auth
    token = db.query(UserEmailToken).filter(UserEmailToken.id == token_id).first()
    if token:
        decrypted = decrypt_field(token.access_token_encrypted, EncryptionKeys.PII)
        print(f"Decrypted token: {decrypted}")
        if decrypted and len(decrypted) > 50 and decrypted.startswith('ya29.'):
            print("Valid Google token.")
        else:
            print("Invalid or empty token.")
    else:
        print("No token found.")
finally:
    db.close()