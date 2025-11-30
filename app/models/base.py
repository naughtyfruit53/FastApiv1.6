from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date  
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import Mapped, mapped_column, relationship  
from sqlalchemy.sql import func  
from app.core.database import Base  
from typing import List, Optional  
from datetime import datetime, date  
  
# All model definitions have been moved to their respective modular files:  
# - user_models.py: PlatformUser, Organization, User, ServiceRole, ServicePermission, ServiceRolePermission, UserServiceRole  
# - customer_models.py: Company, Vendor, Customer, CustomerFile, CustomerInteraction, CustomerSegment, VendorFile  
# - product_models.py: Product, ProductFile, Stock, InventoryTransaction, JobParts, InventoryAlert  
# - system_models.py: AuditLog, EmailNotification, NotificationTemplate, NotificationLog, NotificationPreference, PaymentTerm, OTPVerification  
# - analytics_models.py: ServiceAnalyticsEvent, ReportConfiguration, AnalyticsSummary  
# - service_models.py: Ticket, TicketHistory, TicketAttachment, SLAPolicy, SLATracking, DispatchOrder, DispatchItem, InstallationJob, InstallationTask, CompletionRecord, CustomerFeedback, ServiceClosure  
# - vouchers.py: Voucher models  
  
# This file is now empty of model definitions to prevent duplicates.  