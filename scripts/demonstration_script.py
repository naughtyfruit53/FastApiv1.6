# scripts/demonstration_script.py - Run locally: python scripts/demonstration_script.py

import asyncio
from app.core.database import get_db
from app.models.vouchers import Quotation, QuotationItem, ProformaInvoice, ProformaInvoiceItem
from app.models.base import User, Customer
from app.schemas.vouchers import QuotationCreate, ProformaInvoiceCreate, QuotationItemCreate, ProformaInvoiceItemCreate
from app.api.v1.vouchers.quotation import create_quotation
from app.api.v1.vouchers.proforma_invoice import create_proforma_invoice
from app.services.voucher_service import VoucherNumberService
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
import datetime

async def main():
    db: Session = next(get_db())
    background_tasks = BackgroundTasks()

    # 1. Get user (assume ID 2)
    user = db.get(User, 2)
    if not user:
        print("User not found")
        db.close()
        return

    print("User:", user.email, "Org ID:", user.organization_id)

    # 2. Create or get customer (assume product ID 1 exists)
    customer = db.query(Customer).filter(Customer.organization_id == user.organization_id).first()
    if not customer:
        customer = Customer(
            organization_id=user.organization_id,
            name="Test Customer",
            email="test@customer.com",
            is_active=True
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)

    print("Customer ID:", customer.id)

    # 3. Create Quotation
    quotation_item = QuotationItemCreate(
        product_id=1,  # Assume product ID 1 exists
        quantity=5,
        unit_price=100,
        discount_percentage=0,
        gst_rate=18,
        amount=500,
        total_amount=500,  # Added to match schema
        unit='PCS'  # Added required field
    )

    quotation_create = QuotationCreate(
        customer_id=customer.id,
        date=datetime.date.today(),
        items=[quotation_item],
        voucher_number=''  # Blank to trigger generation
    )

    new_quotation = await create_quotation(
        quotation=quotation_create,
        background_tasks=background_tasks,
        db=db,
        current_user=user
    )

    print("Created Quotation:", new_quotation.voucher_number)

    # 4. Create Proforma Invoice - Added taxable_amount and adjusted values for consistency
    subtotal = 3 * 200  # 600
    discount = subtotal * 5 / 100  # 30
    taxable_amount = subtotal - discount  # 570
    gst_amount = taxable_amount * 18 / 100  # 102.6
    total_amount = taxable_amount + gst_amount  # 672.6

    proforma_item = ProformaInvoiceItemCreate(
        product_id=1,
        quantity=3,
        unit_price=200,
        discount_percentage=5,
        gst_rate=18,
        amount=subtotal,  # Set as subtotal before discount
        taxable_amount=taxable_amount,
        total_amount=total_amount,
        unit='PCS'  # Added required field
    )

    proforma_create = ProformaInvoiceCreate(
        customer_id=customer.id,
        date=datetime.date.today(),
        items=[proforma_item],
        voucher_number=''  # Blank to trigger generation
    )

    new_proforma = await create_proforma_invoice(
        invoice=proforma_create,
        background_tasks=background_tasks,
        db=db,
        current_user=user
    )

    print("Created Proforma Invoice:", new_proforma.voucher_number)

    # 5. List Quotations
    quotations = db.query(Quotation).filter(Quotation.organization_id == user.organization_id).all()
    print("Quotations:")
    for q in quotations:
        print(f"- {q.voucher_number} (ID: {q.id})")

    # 6. List Proforma Invoices
    proformas = db.query(ProformaInvoice).filter(ProformaInvoice.organization_id == user.organization_id).all()
    print("Proforma Invoices:")
    for p in proformas:
        print(f"- {p.voucher_number} (ID: {p.id})")

    db.close()

if __name__ == "__main__":
    asyncio.run(main())