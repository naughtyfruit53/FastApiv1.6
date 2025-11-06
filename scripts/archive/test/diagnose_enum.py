# Revised diagnose_enum.py

from sqlalchemy import text
from app.core.database import SessionLocal

db = SessionLocal()
try:
    result = db.execute(text("SELECT unnest(enum_range(NULL::emailstatus))")).fetchall()
    print("DB enum values for emailstatus:")
    for val in result:
        print(val[0])
finally:
    db.close()