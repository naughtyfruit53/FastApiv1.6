#!/usr/bin/env python3
"""
HR Sample Data Seeder
Generates sample data for HR, Payroll, Recruitment and Talent modules
"""

import os
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import SessionLocal
from app.models.user_models import Organization, User
from app.models.hr_models import (
    EmployeeProfile, AttendanceRecord, LeaveType, 
    LeaveApplication, PerformanceReview
)
from app.models.payroll_models import (
    SalaryStructure, PayrollPeriod, Payslip, TaxSlab, 
    EmployeeLoan, PayrollSettings
)
from app.models.recruitment_models import (
    JobPosting, Candidate, JobApplication, Interview, 
    JobOffer, RecruitmentPipeline
)
from app.models.talent_models import (
    SkillCategory, Skill, EmployeeSkill, TrainingProgram, 
    TrainingSession, TrainingEnrollment, LearningPath, 
    LearningPathProgram, EmployeeLearningPath
)

def create_sample_hr_data():
    """Create comprehensive sample data for HR modules"""
    
    db = SessionLocal()
    
    try:
        print("🏢 Creating HR sample data...")
        
        # Get first organization for demo
        organization = db.query(Organization).first()
        if not organization:
            print("❌ No organization found. Please create an organization first.")
            return
        
        print(f"📊 Using organization: {organization.name}")
        
        # Get admin user for demo
        admin_user = db.query(User).filter(
            User.organization_id == organization.id,
            User.role.in_(["org_admin", "admin"])
        ).first()
        
        if not admin_user:
            print("❌ No admin user found. Please create an admin user first.")
            return
        
        print(f"👤 Using admin user: {admin_user.full_name}")
        
        # Create Leave Types
        print("\n📋 Creating Leave Types...")
        leave_types_data = [
            {"name": "Annual Leave", "code": "AL", "annual_allocation": 21, "description": "Yearly vacation leave"},
            {"name": "Sick Leave", "code": "SL", "annual_allocation": 12, "description": "Medical leave"},
            {"name": "Maternity Leave", "code": "ML", "annual_allocation": 180, "description": "Maternity leave for new mothers"},
            {"name": "Paternity Leave", "code": "PL", "annual_allocation": 15, "description": "Paternity leave for new fathers"},
            {"name": "Emergency Leave", "code": "EL", "annual_allocation": 5, "description": "Emergency family situations"},
        ]
        
        leave_types = []
        for leave_data in leave_types_data:
            # Check if leave type already exists
            existing = db.query(LeaveType).filter(
                LeaveType.organization_id == organization.id,
                LeaveType.code == leave_data["code"]
            ).first()
            
            if not existing:
                leave_type = LeaveType(
                    organization_id=organization.id,
                    **leave_data
                )
                db.add(leave_type)
                leave_types.append(leave_type)
                print(f"   ✅ Created leave type: {leave_data['name']}")
            else:
                leave_types.append(existing)
                print(f"   ⚠️  Leave type already exists: {leave_data['name']}")
        
        db.commit()
        
        # Create Employee Profiles for existing users
        print("\n👥 Creating Employee Profiles...")
        users = db.query(User).filter(User.organization_id == organization.id).limit(10).all()
        
        employees = []
        departments = ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations"]
        job_titles = [
            "Software Engineer", "Senior Developer", "Sales Manager", "Marketing Specialist", 
            "HR Coordinator", "Financial Analyst", "Operations Manager", "Team Lead"
        ]
        
        for i, user in enumerate(users):
            # Check if employee profile already exists
            existing_profile = db.query(EmployeeProfile).filter(
                EmployeeProfile.user_id == user.id
            ).first()
            
            if not existing_profile:
                employee_code = f"EMP{organization.id:03d}{i+1:03d}"
                
                employee = EmployeeProfile(
                    organization_id=organization.id,
                    user_id=user.id,
                    employee_code=employee_code,
                    employee_type=random.choice(["permanent", "contract", "intern"]),
                    date_of_birth=date(1985, 1, 1) + timedelta(days=random.randint(0, 7300)),
                    gender=random.choice(["Male", "Female"]),
                    nationality="Indian",
                    hire_date=date.today() - timedelta(days=random.randint(30, 1000)),
                    job_title=random.choice(job_titles),
                    work_location="Mumbai Office",
                    work_type="office",
                    employment_status="active",
                    created_by_id=admin_user.id
                )
                
                # Update user department
                user.department = random.choice(departments)
                user.designation = employee.job_title
                
                db.add(employee)
                employees.append(employee)
                print(f"   ✅ Created employee profile: {employee_code} - {user.full_name}")
            else:
                employees.append(existing_profile)
                print(f"   ⚠️  Employee profile already exists: {user.full_name}")
        
        db.commit()
        
        # Create Salary Structures
        print("\n💰 Creating Salary Structures...")
        for employee in employees[:5]:  # Create for first 5 employees
            existing_salary = db.query(SalaryStructure).filter(
                SalaryStructure.employee_id == employee.id
            ).first()
            
            if not existing_salary:
                basic_salary = Decimal(str(random.randint(300000, 800000)))  # 3L to 8L basic
                hra = basic_salary * Decimal('0.4')  # 40% HRA
                transport_allowance = Decimal('2000')
                medical_allowance = Decimal('1500')
                special_allowance = Decimal('5000')
                
                gross_salary = basic_salary + hra + transport_allowance + medical_allowance + special_allowance
                
                pf = basic_salary * Decimal('0.12')  # 12% PF
                professional_tax = Decimal('200')
                income_tax = gross_salary * Decimal('0.1')  # 10% tax
                
                total_deductions = pf + professional_tax + income_tax
                net_salary = gross_salary - total_deductions
                
                salary_structure = SalaryStructure(
                    organization_id=organization.id,
                    employee_id=employee.id,
                    structure_name=f"Standard Salary - {employee.employee_code}",
                    effective_from=date.today() - timedelta(days=30),
                    basic_salary=basic_salary,
                    hra=hra,
                    transport_allowance=transport_allowance,
                    medical_allowance=medical_allowance,
                    special_allowance=special_allowance,
                    provident_fund=pf,
                    professional_tax=professional_tax,
                    income_tax=income_tax,
                    gross_salary=gross_salary,
                    total_deductions=total_deductions,
                    net_salary=net_salary,
                    is_approved=True,
                    approved_by_id=admin_user.id,
                    approved_at=datetime.utcnow(),
                    created_by_id=admin_user.id
                )
                
                db.add(salary_structure)
                print(f"   ✅ Created salary structure for: {employee.employee_code}")
        
        db.commit()
        
        # Create Attendance Records for last 30 days
        print("\n📅 Creating Attendance Records...")
        for employee in employees[:3]:  # Create for first 3 employees
            start_date = date.today() - timedelta(days=30)
            
            for day_offset in range(30):
                attendance_date = start_date + timedelta(days=day_offset)
                
                # Skip weekends
                if attendance_date.weekday() >= 5:
                    continue
                
                # Check if attendance already exists
                existing_attendance = db.query(AttendanceRecord).filter(
                    AttendanceRecord.employee_id == employee.id,
                    AttendanceRecord.attendance_date == attendance_date
                ).first()
                
                if not existing_attendance:
                    # 90% chance of being present
                    if random.random() < 0.9:
                        status = "present"
                        check_in_time = datetime.strptime("09:00", "%H:%M").time()
                        check_out_time = datetime.strptime("18:00", "%H:%M").time()
                        total_hours = Decimal('8.0')
                        overtime_hours = Decimal(str(random.randint(0, 2)))
                    else:
                        status = random.choice(["absent", "on_leave"])
                        check_in_time = None
                        check_out_time = None
                        total_hours = Decimal('0')
                        overtime_hours = Decimal('0')
                    
                    attendance = AttendanceRecord(
                        organization_id=organization.id,
                        employee_id=employee.id,
                        attendance_date=attendance_date,
                        check_in_time=check_in_time,
                        check_out_time=check_out_time,
                        total_hours=total_hours,
                        overtime_hours=overtime_hours,
                        attendance_status=status,
                        is_approved=True,
                        approved_by_id=admin_user.id,
                        approved_at=datetime.utcnow()
                    )
                    
                    db.add(attendance)
        
        print(f"   ✅ Created attendance records for last 30 days")
        db.commit()
        
        # Create Leave Applications
        print("\n🏖️ Creating Leave Applications...")
        for i, employee in enumerate(employees[:4]):
            # Create 2-3 leave applications per employee
            for j in range(random.randint(2, 3)):
                leave_type = random.choice(leave_types)
                start_date = date.today() + timedelta(days=random.randint(10, 60))
                total_days = random.randint(2, 7)
                end_date = start_date + timedelta(days=total_days - 1)
                
                leave_app = LeaveApplication(
                    organization_id=organization.id,
                    employee_id=employee.id,
                    leave_type_id=leave_type.id,
                    start_date=start_date,
                    end_date=end_date,
                    total_days=total_days,
                    reason=f"Personal work - {leave_type.name}",
                    status=random.choice(["pending", "approved", "rejected"]),
                    approved_by_id=admin_user.id if random.random() > 0.3 else None,
                    approved_date=datetime.utcnow() if random.random() > 0.3 else None
                )
                
                db.add(leave_app)
        
        print(f"   ✅ Created leave applications")
        db.commit()
        
        # Create Performance Reviews
        print("\n📊 Creating Performance Reviews...")
        for employee in employees[:3]:
            review = PerformanceReview(
                organization_id=organization.id,
                employee_id=employee.id,
                reviewer_id=admin_user.id,
                review_period_start=date(2023, 4, 1),
                review_period_end=date(2024, 3, 31),
                review_type="annual",
                overall_rating=Decimal(str(random.uniform(3.0, 5.0))),
                technical_skills_rating=Decimal(str(random.uniform(3.0, 5.0))),
                communication_rating=Decimal(str(random.uniform(3.0, 5.0))),
                leadership_rating=Decimal(str(random.uniform(3.0, 5.0))),
                teamwork_rating=Decimal(str(random.uniform(3.0, 5.0))),
                achievements="Completed all assigned projects successfully. Demonstrated strong technical skills.",
                areas_of_improvement="Could improve time management and client communication skills.",
                goals_next_period="Focus on leadership development and taking on more complex projects.",
                status="completed",
                submitted_date=datetime.utcnow() - timedelta(days=random.randint(10, 30))
            )
            
            db.add(review)
        
        print(f"   ✅ Created performance reviews")
        db.commit()
        
        # Create Payroll Settings
        print("\n⚙️ Creating Payroll Settings...")
        existing_settings = db.query(PayrollSettings).filter(
            PayrollSettings.organization_id == organization.id
        ).first()
        
        if not existing_settings:
            payroll_settings = PayrollSettings(
                organization_id=organization.id,
                pay_frequency="monthly",
                payroll_start_day=1,
                payroll_cut_off_day=25,
                working_days_per_month=22,
                working_hours_per_day=Decimal('8'),
                overtime_multiplier=Decimal('1.5'),
                pf_enabled=True,
                employee_pf_rate=Decimal('12'),
                employer_pf_rate=Decimal('12'),
                pf_ceiling=Decimal('15000'),
                pt_enabled=True,
                pt_amount=Decimal('200'),
                pt_state="Maharashtra",
                hra_enabled=True,
                hra_percentage=Decimal('40'),
                metro_hra_percentage=Decimal('50'),
                updated_by_id=admin_user.id
            )
            
            db.add(payroll_settings)
            print(f"   ✅ Created payroll settings")
        else:
            print(f"   ⚠️  Payroll settings already exist")
        
        db.commit()
        
        # Create Tax Slabs
        print("\n💸 Creating Tax Slabs...")
        tax_slabs_data = [
            {"slab_name": "No Tax", "min_amount": 0, "max_amount": 250000, "tax_rate": 0},
            {"slab_name": "5% Slab", "min_amount": 250001, "max_amount": 500000, "tax_rate": 5},
            {"slab_name": "10% Slab", "min_amount": 500001, "max_amount": 750000, "tax_rate": 10},
            {"slab_name": "15% Slab", "min_amount": 750001, "max_amount": 1000000, "tax_rate": 15},
            {"slab_name": "20% Slab", "min_amount": 1000001, "max_amount": 1250000, "tax_rate": 20},
            {"slab_name": "25% Slab", "min_amount": 1250001, "max_amount": 1500000, "tax_rate": 25},
            {"slab_name": "30% Slab", "min_amount": 1500001, "max_amount": None, "tax_rate": 30},
        ]
        
        for slab_data in tax_slabs_data:
            existing_slab = db.query(TaxSlab).filter(
                TaxSlab.organization_id == organization.id,
                TaxSlab.slab_name == slab_data["slab_name"],
                TaxSlab.financial_year == "2023-24"
            ).first()
            
            if not existing_slab:
                tax_slab = TaxSlab(
                    organization_id=organization.id,
                    financial_year="2023-24",
                    **slab_data
                )
                db.add(tax_slab)
        
        print(f"   ✅ Created tax slabs for FY 2023-24")
        db.commit()
        
        # Create Job Postings
        print("\n💼 Creating Job Postings...")
        jobs_data = [
            {
                "job_title": "Senior Software Engineer",
                "job_code": "SSE001",
                "department": "Engineering",
                "description": "We are looking for a Senior Software Engineer to join our growing team.",
                "min_experience": 3,
                "max_experience": 6,
                "min_salary": 800000,
                "max_salary": 1200000
            },
            {
                "job_title": "Marketing Manager",
                "job_code": "MM001", 
                "department": "Marketing",
                "description": "Lead our marketing initiatives and drive brand growth.",
                "min_experience": 2,
                "max_experience": 5,
                "min_salary": 600000,
                "max_salary": 900000
            },
            {
                "job_title": "Sales Executive",
                "job_code": "SE001",
                "department": "Sales", 
                "description": "Drive sales growth and build strong client relationships.",
                "min_experience": 1,
                "max_experience": 3,
                "min_salary": 400000,
                "max_salary": 600000
            }
        ]
        
        for job_data in jobs_data:
            existing_job = db.query(JobPosting).filter(
                JobPosting.organization_id == organization.id,
                JobPosting.job_code == job_data["job_code"]
            ).first()
            
            if not existing_job:
                job_posting = JobPosting(
                    organization_id=organization.id,
                    job_title=job_data["job_title"],
                    job_code=job_data["job_code"],
                    department=job_data["department"],
                    location="Mumbai, India",
                    employment_type="full_time",
                    job_description=job_data["description"],
                    responsibilities="Key responsibilities include project delivery, team collaboration, and client communication.",
                    requirements="Bachelor's degree in relevant field with strong communication skills.",
                    qualifications="Relevant experience and technical expertise required.",
                    min_experience=job_data["min_experience"],
                    max_experience=job_data["max_experience"],
                    min_salary=Decimal(str(job_data["min_salary"])),
                    max_salary=Decimal(str(job_data["max_salary"])),
                    status="active",
                    hiring_manager_id=admin_user.id,
                    posted_by_id=admin_user.id,
                    application_deadline=date.today() + timedelta(days=30)
                )
                
                db.add(job_posting)
                print(f"   ✅ Created job posting: {job_data['job_title']}")
        
        db.commit()
        
        # Create Skill Categories and Skills
        print("\n🎯 Creating Skills and Categories...")
        skill_categories_data = [
            {"name": "Technical Skills", "description": "Programming and technical competencies"},
            {"name": "Soft Skills", "description": "Communication and interpersonal skills"},
            {"name": "Leadership", "description": "Management and leadership capabilities"},
        ]
        
        skill_categories = []
        for cat_data in skill_categories_data:
            existing_cat = db.query(SkillCategory).filter(
                SkillCategory.organization_id == organization.id,
                SkillCategory.name == cat_data["name"]
            ).first()
            
            if not existing_cat:
                category = SkillCategory(
                    organization_id=organization.id,
                    **cat_data
                )
                db.add(category)
                skill_categories.append(category)
            else:
                skill_categories.append(existing_cat)
        
        db.commit()
        
        # Create Skills
        skills_data = [
            {"name": "Python", "category": "Technical Skills", "type": "technical"},
            {"name": "JavaScript", "category": "Technical Skills", "type": "technical"},
            {"name": "Communication", "category": "Soft Skills", "type": "soft"},
            {"name": "Team Management", "category": "Leadership", "type": "soft"},
            {"name": "Project Management", "category": "Leadership", "type": "soft"},
        ]
        
        for skill_data in skills_data:
            category = next((c for c in skill_categories if c.name == skill_data["category"]), None)
            
            if category:
                existing_skill = db.query(Skill).filter(
                    Skill.organization_id == organization.id,
                    Skill.name == skill_data["name"]
                ).first()
                
                if not existing_skill:
                    skill = Skill(
                        organization_id=organization.id,
                        name=skill_data["name"],
                        skill_type=skill_data["type"],
                        category_id=category.id
                    )
                    db.add(skill)
        
        print(f"   ✅ Created skills and categories")
        db.commit()
        
        print("\n✅ HR sample data creation completed successfully!")
        print("\n📊 Summary of created data:")
        print(f"   • {len(leave_types)} Leave Types")
        print(f"   • {len(employees)} Employee Profiles")
        print(f"   • Salary Structures for 5 employees")
        print(f"   • Attendance records for last 30 days")
        print(f"   • Leave applications")
        print(f"   • Performance reviews")
        print(f"   • Payroll settings")
        print(f"   • Tax slabs")
        print(f"   • Job postings")
        print(f"   • Skills and categories")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting HR Sample Data Creation...")
    success = create_sample_hr_data()
    
    if success:
        print("\n🎉 HR sample data created successfully!")
        print("You can now:")
        print("   • View employees at /hr/employees")
        print("   • Check attendance at /hr/attendance") 
        print("   • Review leave applications at /hr/leaves")
        print("   • Access payroll at /payroll")
        print("   • Browse job postings at /recruitment/jobs")
    else:
        print("\n💥 Failed to create sample data. Check the errors above.")
        sys.exit(1)