# scripts/list_all_users.py

from app.core.database import get_db
from app.models.base import User
from sqlalchemy.orm import Session

db: Session = next(get_db())
users = db.query(User).all()

print("All users:")
for u in users:
    print(f"- ID: {u.id}, Email: {u.email}, Org ID: {u.organization_id}, Super Admin: {u.is_super_admin}")

db.close()