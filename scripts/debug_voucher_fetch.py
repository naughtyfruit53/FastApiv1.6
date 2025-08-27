# scripts/debug_voucher_fetch.py

from app.core.database import get_db
from app.models.base import User
from app.models.vouchers import Quotation, ProformaInvoice
from sqlalchemy.orm import Session

# Hardcoded email - replace if needed
email = 'potymatic@gmail.com'

db: Session = next(get_db())

user = db.query(User).filter(User.email == email).first()
if not user:
    print(f"No user found with email: {email}")
else:
    print(f"User ID: {user.id}, Org ID: {user.organization_id}")

    quotations = db.query(Quotation).filter(Quotation.organization_id == user.organization_id).all()
    print(f"Found {len(quotations)} quotations for org {user.organization_id}:")
    for q in quotations:
        print(f"- ID: {q.id}, Number: {q.voucher_number}, Created By: {q.created_by}, Date: {q.date}")

    proforma_invoices = db.query(ProformaInvoice).filter(ProformaInvoice.organization_id == user.organization_id).all()
    print(f"Found {len(proforma_invoices)} proforma invoices for org {user.organization_id}:")
    for pi in proforma_invoices:
        print(f"- ID: {pi.id}, Number: {pi.voucher_number}, Created By: {pi.created_by}, Date: {pi.date}")

db.close()