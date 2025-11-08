# delete_old_token.py - Run this locally to delete the old token
from app.core.database import SessionLocal
from app.models.oauth_models import UserEmailToken

db = SessionLocal()
try:
    token_id = 2  # Your token ID
    token = db.query(UserEmailToken).filter(UserEmailToken.id == token_id).first()
    if token:
        db.delete(token)
        db.commit()
        print("Old token deleted.")
    else:
        print("No token found.")
finally:
    db.close()