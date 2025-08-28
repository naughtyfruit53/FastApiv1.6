# app/models/talent_models.py

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

# Skills Management
class SkillCategory(Base):
    """Categories for organizing skills"""
    __tablename__ = "skill_categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_skill_category_organization_id"), nullable=False, index=True)
    
    # Category details
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # For UI display
    
    # Hierarchy
    parent_category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("skill_categories.id", name="fk_skill_category_parent_id"), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
    parent_category: Mapped[Optional["SkillCategory"]] = relationship("SkillCategory", remote_side=[id])
    skills: Mapped[List["Skill"]] = relationship("Skill", back_populates="category")

    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='uq_skill_category_org_name'),
        Index('idx_skill_category_org_active', 'organization_id', 'is_active'),
        {'extend_existing': True}
    )

class Skill(Base):
    """Skills master data"""
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_skill_organization_id"), nullable=False, index=True)
    
    # Skill details
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    skill_type: Mapped[str] = mapped_column(String, nullable=False, default="technical")  # technical, soft, language, certification
    
    # Category
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("skill_categories.id", name="fk_skill_category_id"), nullable=True)
    
    # Proficiency levels (JSON for flexibility)
    proficiency_levels: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=lambda: {
        "1": "Beginner",
        "2": "Intermediate", 
        "3": "Advanced",
        "4": "Expert",
        "5": "Master"
    })
    
    # Assessment criteria
    assessment_criteria: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_certifiable: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
    category: Mapped[Optional["SkillCategory"]] = relationship("SkillCategory", back_populates="skills")
    employee_skills: Mapped[List["EmployeeSkill"]] = relationship("EmployeeSkill", back_populates="skill")

    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='uq_skill_org_name'),
        Index('idx_skill_org_type', 'organization_id', 'skill_type'),
        Index('idx_skill_active', 'is_active'),
        {'extend_existing': True}
    )

class EmployeeSkill(Base):
    """Employee skill assessments and proficiency tracking"""
    __tablename__ = "employee_skills"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_employee_skill_organization_id"), nullable=False, index=True)
    
    # References
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employee_profiles.id", name="fk_employee_skill_employee_id"), nullable=False, index=True)
    skill_id: Mapped[int] = mapped_column(Integer, ForeignKey("skills.id", name="fk_employee_skill_skill_id"), nullable=False, index=True)
    
    # Proficiency details
    proficiency_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)  # 1-5 scale
    self_assessment: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    manager_assessment: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    peer_assessment: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Assessment details
    assessed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    assessed_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_employee_skill_assessed_by_id"), nullable=True)
    assessment_method: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # test, project, observation, certification
    
    # Experience and certification
    years_of_experience: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)
    certification_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    certification_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    certification_expiry: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Learning goals
    target_proficiency: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    target_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    learning_plan: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Notes and evidence
    assessment_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence_links: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Links to projects, certificates, etc.
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
    employee: Mapped["app.models.hr_models.EmployeeProfile"] = relationship("app.models.hr_models.EmployeeProfile")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="employee_skills")
    assessed_by: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User")

    __table_args__ = (
        UniqueConstraint('employee_id', 'skill_id', name='uq_employee_skill_emp_skill'),
        Index('idx_employee_skill_org_employee', 'organization_id', 'employee_id'),
        Index('idx_employee_skill_proficiency', 'proficiency_level'),
        {'extend_existing': True}
    )

# Training Management
class TrainingProgram(Base):
    """Training programs and courses"""
    __tablename__ = "training_programs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_training_program_organization_id"), nullable=False, index=True)
    
    # Program details
    program_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    program_code: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    objectives: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Program classification
    category: Mapped[str] = mapped_column(String, nullable=False, default="technical")  # technical, soft_skills, compliance, leadership
    level: Mapped[str] = mapped_column(String, nullable=False, default="intermediate")  # beginner, intermediate, advanced
    delivery_method: Mapped[str] = mapped_column(String, nullable=False, default="instructor_led")  # instructor_led, online, blended, self_paced
    
    # Duration and structure
    duration_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_participants: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    min_participants: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=1)
    
    # Prerequisites and targets
    prerequisites: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_audience: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    required_skills: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Required skill IDs and levels
    target_skills: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Skills that will be developed
    
    # Content and materials
    curriculum: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Detailed curriculum structure
    materials: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Links to materials, documents
    assessment_criteria: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Provider and cost
    provider_type: Mapped[str] = mapped_column(String, nullable=False, default="internal")  # internal, external, vendor
    provider_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    provider_contact: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cost_per_participant: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="INR")
    
    # Certification
    provides_certification: Mapped[bool] = mapped_column(Boolean, default=False)
    certification_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    certification_validity_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Status and approval
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft")  # draft, approved, active, suspended, archived
    approved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_training_program_approved_by_id"), nullable=True)
    approved_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Effectiveness tracking
    overall_rating: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)  # Average participant rating
    completion_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)  # Percentage
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_training_program_created_by_id"), nullable=True)

    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
    approved_by: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User", foreign_keys=[approved_by_id])
    created_by: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User", foreign_keys=[created_by_id])
    
    # Training relationships
    sessions: Mapped[List["TrainingSession"]] = relationship("TrainingSession", back_populates="program")
    enrollments: Mapped[List["TrainingEnrollment"]] = relationship("TrainingEnrollment", back_populates="program")

    __table_args__ = (
        UniqueConstraint('organization_id', 'program_code', name='uq_training_program_org_code'),
        Index('idx_training_program_org_status', 'organization_id', 'status'),
        Index('idx_training_program_category', 'category'),
        {'extend_existing': True}
    )

class TrainingSession(Base):
    """Scheduled training sessions"""
    __tablename__ = "training_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_training_session_organization_id"), nullable=False, index=True)
    
    # Program reference
    program_id: Mapped[int] = mapped_column(Integer, ForeignKey("training_programs.id", name="fk_training_session_program_id"), nullable=False, index=True)
    
    # Session details
    session_name: Mapped[str] = mapped_column(String, nullable=False)
    session_code: Mapped[str] = mapped_column(String, nullable=False, index=True)
    
    # Scheduling
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Location and delivery
    delivery_method: Mapped[str] = mapped_column(String, nullable=False, default="instructor_led")
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    venue_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meeting_link: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Instructor and capacity
    instructor_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_training_session_instructor_id"), nullable=True)
    external_instructor: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    max_participants: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    enrolled_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Status
    status: Mapped[str] = mapped_column(String, nullable=False, default="scheduled")  # scheduled, in_progress, completed, cancelled
    
    # Registration
    registration_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    registration_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    auto_approve_registration: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Session results
    completion_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    average_rating: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    # Materials and resources
    session_materials: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    prerequisites_checked: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
    program: Mapped["TrainingProgram"] = relationship("TrainingProgram", back_populates="sessions")
    instructor: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User")
    enrollments: Mapped[List["TrainingEnrollment"]] = relationship("TrainingEnrollment", back_populates="session")

    __table_args__ = (
        UniqueConstraint('organization_id', 'session_code', name='uq_training_session_org_code'),
        Index('idx_training_session_org_dates', 'organization_id', 'start_date', 'end_date'),
        Index('idx_training_session_status', 'status'),
        {'extend_existing': True}
    )

class TrainingEnrollment(Base):
    """Employee enrollment in training sessions"""
    __tablename__ = "training_enrollments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_training_enrollment_organization_id"), nullable=False, index=True)
    
    # References
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employee_profiles.id", name="fk_training_enrollment_employee_id"), nullable=False, index=True)
    program_id: Mapped[int] = mapped_column(Integer, ForeignKey("training_programs.id", name="fk_training_enrollment_program_id"), nullable=False, index=True)
    session_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("training_sessions.id", name="fk_training_enrollment_session_id"), nullable=True, index=True)
    
    # Enrollment details
    enrollment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    enrollment_type: Mapped[str] = mapped_column(String, nullable=False, default="voluntary")  # voluntary, mandatory, recommended
    enrollment_source: Mapped[str] = mapped_column(String, nullable=False, default="self")  # self, manager, hr, system
    
    # Status and approval
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")  # pending, approved, rejected, enrolled, completed, dropped
    approved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_training_enrollment_approved_by_id"), nullable=True)
    approved_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Participation tracking
    attendance_percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    participation_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    assignment_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    final_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    
    # Completion details
    completed_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    certificate_issued: Mapped[bool] = mapped_column(Boolean, default=False)
    certificate_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    certificate_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Feedback and evaluation
    participant_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5 stars
    participant_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    instructor_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Cost tracking
    cost_allocated: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    budget_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
    employee: Mapped["app.models.hr_models.EmployeeProfile"] = relationship("app.models.hr_models.EmployeeProfile")
    program: Mapped["TrainingProgram"] = relationship("TrainingProgram", back_populates="enrollments")
    session: Mapped[Optional["TrainingSession"]] = relationship("TrainingSession", back_populates="enrollments")
    approved_by: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User")

    __table_args__ = (
        UniqueConstraint('employee_id', 'program_id', 'session_id', name='uq_training_enrollment_emp_prog_session'),
        Index('idx_training_enrollment_org_employee', 'organization_id', 'employee_id'),
        Index('idx_training_enrollment_status', 'status'),
        {'extend_existing': True}
    )

# Learning Path Management
class LearningPath(Base):
    """Structured learning paths for career development"""
    __tablename__ = "learning_paths"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_learning_path_organization_id"), nullable=False, index=True)
    
    # Path details
    path_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    target_role: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    career_level: Mapped[str] = mapped_column(String, nullable=False, default="intermediate")  # junior, intermediate, senior, expert
    
    # Path structure
    estimated_duration_months: Mapped[int] = mapped_column(Integer, nullable=False)
    difficulty_level: Mapped[str] = mapped_column(String, nullable=False, default="intermediate")
    prerequisites: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Skills development
    target_skills: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Skills and target proficiency levels
    milestone_skills: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Key milestones
    
    # Path configuration
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=False)
    is_self_paced: Mapped[bool] = mapped_column(Boolean, default=True)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Status
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft")  # draft, active, suspended, archived
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_learning_path_created_by_id"), nullable=True)

    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
    created_by: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User")
    
    # Learning relationships
    path_programs: Mapped[List["LearningPathProgram"]] = relationship("LearningPathProgram", back_populates="learning_path")
    employee_paths: Mapped[List["EmployeeLearningPath"]] = relationship("EmployeeLearningPath", back_populates="learning_path")

    __table_args__ = (
        UniqueConstraint('organization_id', 'path_name', name='uq_learning_path_org_name'),
        Index('idx_learning_path_org_status', 'organization_id', 'status'),
        Index('idx_learning_path_level', 'career_level'),
        {'extend_existing': True}
    )

class LearningPathProgram(Base):
    """Programs included in learning paths"""
    __tablename__ = "learning_path_programs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # References
    learning_path_id: Mapped[int] = mapped_column(Integer, ForeignKey("learning_paths.id", name="fk_learning_path_program_path_id"), nullable=False, index=True)
    program_id: Mapped[int] = mapped_column(Integer, ForeignKey("training_programs.id", name="fk_learning_path_program_program_id"), nullable=False, index=True)
    
    # Sequence and requirements
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True)
    prerequisite_programs: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Program IDs that must be completed first
    
    # Completion criteria
    minimum_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    requires_certification: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    learning_path: Mapped["LearningPath"] = relationship("LearningPath", back_populates="path_programs")
    program: Mapped["TrainingProgram"] = relationship("TrainingProgram")

    __table_args__ = (
        UniqueConstraint('learning_path_id', 'program_id', name='uq_learning_path_program'),
        Index('idx_learning_path_program_sequence', 'learning_path_id', 'sequence_order'),
        {'extend_existing': True}
    )

class EmployeeLearningPath(Base):
    """Employee enrollment in learning paths"""
    __tablename__ = "employee_learning_paths"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_employee_learning_path_organization_id"), nullable=False, index=True)
    
    # References
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employee_profiles.id", name="fk_employee_learning_path_employee_id"), nullable=False, index=True)
    learning_path_id: Mapped[int] = mapped_column(Integer, ForeignKey("learning_paths.id", name="fk_employee_learning_path_path_id"), nullable=False, index=True)
    
    # Enrollment details
    enrolled_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    target_completion_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    assigned_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_employee_learning_path_assigned_by_id"), nullable=True)
    
    # Progress tracking
    status: Mapped[str] = mapped_column(String, nullable=False, default="in_progress")  # in_progress, completed, paused, dropped
    progress_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    completed_programs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_programs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Completion details
    completed_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    overall_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    
    # Notes and feedback
    employee_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    manager_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
    employee: Mapped["app.models.hr_models.EmployeeProfile"] = relationship("app.models.hr_models.EmployeeProfile")
    learning_path: Mapped["LearningPath"] = relationship("LearningPath", back_populates="employee_paths")
    assigned_by: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User")

    __table_args__ = (
        UniqueConstraint('employee_id', 'learning_path_id', name='uq_employee_learning_path'),
        Index('idx_employee_learning_path_org_employee', 'organization_id', 'employee_id'),
        Index('idx_employee_learning_path_status', 'status'),
        {'extend_existing': True}
    )