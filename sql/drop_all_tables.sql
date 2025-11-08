-- ============================================================================
-- DROP ALL TABLES - Complete Database Reset Script
-- ============================================================================
-- 
-- WARNING: This script will PERMANENTLY DELETE all data in the database!
-- 
-- Purpose: Complete database reset for Supabase/PostgreSQL
-- Use Case: Fresh start after major schema changes or for testing
--
-- Usage:
--   1. Backup your database first (if needed):
--      pg_dump -U postgres -d your_database > backup_$(date +%Y%m%d_%H%M%S).sql
--
--   2. Connect to your database:
--      psql -U postgres -d your_database
--
--   3. Run this script:
--      \i sql/drop_all_tables.sql
--
--   4. Run migrations to recreate schema:
--      alembic upgrade head
--
--   5. Run seeding to populate baseline data:
--      python scripts/seed_all.py
--
-- ============================================================================

-- Confirmation check (comment out the line below to proceed)
-- DO $$ BEGIN RAISE EXCEPTION 'SAFETY CHECK: Comment out this line to proceed with dropping all tables'; END $$;

-- Drop all tables in correct order (respecting foreign key dependencies)
-- This script attempts to drop tables in reverse dependency order

BEGIN;

-- Disable all triggers temporarily to avoid foreign key issues
SET session_replication_role = 'replica';

-- Drop tables in reverse dependency order
-- Start with dependent tables first, then parent tables

-- ============================================================================
-- Step 1: Drop Junction/Association Tables
-- ============================================================================
DROP TABLE IF EXISTS user_service_roles CASCADE;
DROP TABLE IF EXISTS service_role_permissions CASCADE;
DROP TABLE IF EXISTS org_subentitlements CASCADE;
DROP TABLE IF EXISTS learning_path_programs CASCADE;
DROP TABLE IF EXISTS employee_learning_paths CASCADE;
DROP TABLE IF EXISTS training_enrollments CASCADE;
DROP TABLE IF EXISTS employee_skills CASCADE;

-- ============================================================================
-- Step 2: Drop Application-Specific Tables
-- ============================================================================

-- HR & Recruitment
DROP TABLE IF EXISTS performance_reviews CASCADE;
DROP TABLE IF EXISTS leave_applications CASCADE;
DROP TABLE IF EXISTS attendance_records CASCADE;
DROP TABLE IF EXISTS employee_profiles CASCADE;
DROP TABLE IF EXISTS leave_types CASCADE;
DROP TABLE IF EXISTS job_offers CASCADE;
DROP TABLE IF EXISTS interviews CASCADE;
DROP TABLE IF EXISTS job_applications CASCADE;
DROP TABLE IF EXISTS candidates CASCADE;
DROP TABLE IF EXISTS job_postings CASCADE;
DROP TABLE IF EXISTS recruitment_pipelines CASCADE;

-- Payroll
DROP TABLE IF EXISTS payslips CASCADE;
DROP TABLE IF EXISTS employee_loans CASCADE;
DROP TABLE IF EXISTS payroll_periods CASCADE;
DROP TABLE IF EXISTS salary_structures CASCADE;
DROP TABLE IF EXISTS tax_slabs CASCADE;
DROP TABLE IF EXISTS payroll_settings CASCADE;

-- Talent Management
DROP TABLE IF EXISTS training_sessions CASCADE;
DROP TABLE IF EXISTS training_programs CASCADE;
DROP TABLE IF EXISTS learning_paths CASCADE;
DROP TABLE IF EXISTS skills CASCADE;
DROP TABLE IF EXISTS skill_categories CASCADE;

-- Manufacturing
DROP TABLE IF EXISTS quality_inspections CASCADE;
DROP TABLE IF EXISTS production_logs CASCADE;
DROP TABLE IF EXISTS work_order_items CASCADE;
DROP TABLE IF EXISTS work_orders CASCADE;
DROP TABLE IF EXISTS production_orders CASCADE;
DROP TABLE IF EXISTS bill_of_materials CASCADE;
DROP TABLE IF EXISTS jobwork_orders CASCADE;
DROP TABLE IF EXISTS manufacturing_settings CASCADE;

-- Inventory & Stock
DROP TABLE IF EXISTS stock_movements CASCADE;
DROP TABLE IF EXISTS stock_adjustments CASCADE;
DROP TABLE IF EXISTS stock_locations CASCADE;
DROP TABLE IF EXISTS inventory_items CASCADE;

-- Finance & Accounting
DROP TABLE IF EXISTS voucher_items CASCADE;
DROP TABLE IF EXISTS vouchers CASCADE;
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS bills CASCADE;
DROP TABLE IF EXISTS journal_entries CASCADE;
DROP TABLE IF EXISTS ledger_entries CASCADE;
DROP TABLE IF EXISTS chart_of_accounts CASCADE;
DROP TABLE IF EXISTS financial_periods CASCADE;
DROP TABLE IF EXISTS tax_configurations CASCADE;

-- CRM & Service
DROP TABLE IF EXISTS service_tickets CASCADE;
DROP TABLE IF EXISTS appointments CASCADE;
DROP TABLE IF EXISTS opportunities CASCADE;
DROP TABLE IF EXISTS leads CASCADE;
DROP TABLE IF EXISTS contacts CASCADE;
DROP TABLE IF EXISTS marketing_campaigns CASCADE;
DROP TABLE IF EXISTS email_templates CASCADE;

-- Projects & Tasks
DROP TABLE IF EXISTS task_comments CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS project_members CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS calendar_events CASCADE;

-- Products & Vendors
DROP TABLE IF EXISTS product_variants CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS vendors CASCADE;
DROP TABLE IF EXISTS companies CASCADE;

-- Assets & Transport
DROP TABLE IF EXISTS asset_maintenance CASCADE;
DROP TABLE IF EXISTS assets CASCADE;
DROP TABLE IF EXISTS transport_bookings CASCADE;
DROP TABLE IF EXISTS vehicles CASCADE;

-- Email & Notifications
DROP TABLE IF EXISTS email_accounts CASCADE;
DROP TABLE IF EXISTS email_messages CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;

-- Settings & Configuration
DROP TABLE IF EXISTS voucher_format_templates CASCADE;
DROP TABLE IF EXISTS organization_settings CASCADE;
DROP TABLE IF EXISTS system_settings CASCADE;

-- OAuth & Authentication
DROP TABLE IF EXISTS oauth_tokens CASCADE;
DROP TABLE IF EXISTS refresh_tokens CASCADE;
DROP TABLE IF EXISTS password_reset_tokens CASCADE;

-- ============================================================================
-- Step 3: Drop Core/Base Tables
-- ============================================================================

-- RBAC
DROP TABLE IF EXISTS service_permissions CASCADE;
DROP TABLE IF EXISTS service_roles CASCADE;

-- Entitlements
DROP TABLE IF EXISTS entitlement_events CASCADE;
DROP TABLE IF EXISTS submodules CASCADE;
DROP TABLE IF EXISTS modules CASCADE;
DROP TABLE IF EXISTS org_entitlements CASCADE;

-- Users & Organizations
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;

-- ============================================================================
-- Step 4: Drop Alembic Version Table
-- ============================================================================
DROP TABLE IF EXISTS alembic_version CASCADE;

-- ============================================================================
-- Step 5: Re-enable Triggers
-- ============================================================================
SET session_replication_role = 'origin';

COMMIT;

-- ============================================================================
-- Verification: List remaining tables
-- ============================================================================
SELECT 
    schemaname,
    tablename
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- If any tables remain, they may need to be dropped manually
-- You can use: DROP TABLE IF EXISTS <table_name> CASCADE;

-- ============================================================================
-- Post-Reset Steps
-- ============================================================================
-- 1. Run migrations: alembic upgrade head
-- 2. Seed baseline data: python scripts/seed_all.py
-- ============================================================================
