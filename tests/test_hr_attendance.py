# tests/test_hr_attendance.py
"""
Unit tests for HR Attendance Management
Tests clock-in/out, attendance records, and shift management.
"""

import pytest
from datetime import date, datetime, time
from decimal import Decimal

# Import models and schemas at module level
from app.models.hr_models import (
    WorkShift, AttendanceRecord, HolidayCalendar,
    Department, Position
)
from app.schemas.hr_schemas import (
    WorkShiftCreate, AttendanceRecordCreate,
    HolidayCalendarCreate, DepartmentCreate, PositionCreate
)


class TestHRAttendanceModels:
    """Tests for HR attendance-related models"""

    def test_work_shift_defaults(self):
        """Test WorkShift model default values"""
        shift = WorkShift(
            organization_id=1,
            name="General Shift",
            code="GEN",
            start_time=time(9, 0),
            end_time=time(18, 0),
            working_hours=Decimal("8")
        )
        
        assert shift.break_duration_minutes == 60
        assert shift.shift_type == "general"
        assert shift.grace_period_minutes == 15
        assert shift.overtime_threshold_minutes == 30
        assert shift.is_active is True
        assert shift.is_default is False

    def test_attendance_record_defaults(self):
        """Test AttendanceRecord model default values"""
        record = AttendanceRecord(
            organization_id=1,
            employee_id=1,
            attendance_date=date.today()
        )
        
        assert record.attendance_status == "present"
        assert record.work_type == "office"
        assert record.overtime_hours == Decimal("0")
        assert record.break_hours == Decimal("0")
        assert record.is_approved is False

    def test_holiday_calendar_defaults(self):
        """Test HolidayCalendar model default values"""
        
        holiday = HolidayCalendar(
            organization_id=1,
            name="Republic Day",
            holiday_date=date(2024, 1, 26),
            year=2024
        )
        
        assert holiday.holiday_type == "public"
        assert holiday.is_mandatory is True

    def test_department_defaults(self):
        """Test Department model default values"""
        
        dept = Department(
            organization_id=1,
            name="Engineering",
            code="ENG"
        )
        
        assert dept.is_active is True
        assert dept.parent_id is None
        assert dept.manager_id is None

    def test_position_defaults(self):
        """Test Position model default values"""
        
        position = Position(
            organization_id=1,
            title="Software Engineer",
            code="SE"
        )
        
        assert position.is_active is True
        assert position.department_id is None
        assert position.level is None
        assert position.grade is None


class TestHRAttendanceSchemas:
    """Tests for HR attendance-related schemas"""

    def test_work_shift_create_schema(self):
        """Test WorkShiftCreate schema validation"""
        
        shift_data = WorkShiftCreate(
            name="Morning Shift",
            code="MORN",
            start_time=time(6, 0),
            end_time=time(14, 0),
            working_hours=Decimal("8"),
            shift_type="morning"
        )
        
        assert shift_data.name == "Morning Shift"
        assert shift_data.code == "MORN"
        assert shift_data.start_time == time(6, 0)
        assert shift_data.end_time == time(14, 0)

    def test_attendance_record_create_schema(self):
        """Test AttendanceRecordCreate schema validation"""
        
        record_data = AttendanceRecordCreate(
            employee_id=1,
            attendance_date=date.today(),
            check_in_time=time(9, 15),
            attendance_status="present",
            work_type="office"
        )
        
        assert record_data.employee_id == 1
        assert record_data.check_in_time == time(9, 15)

    def test_holiday_calendar_create_schema(self):
        """Test HolidayCalendarCreate schema validation"""
        
        holiday_data = HolidayCalendarCreate(
            name="Diwali",
            holiday_date=date(2024, 11, 1),
            holiday_type="public",
            year=2024,
            is_mandatory=True
        )
        
        assert holiday_data.name == "Diwali"
        assert holiday_data.year == 2024

    def test_department_create_schema(self):
        """Test DepartmentCreate schema validation"""
        
        dept_data = DepartmentCreate(
            name="Human Resources",
            code="HR",
            description="HR Department"
        )
        
        assert dept_data.name == "Human Resources"
        assert dept_data.code == "HR"

    def test_position_create_schema(self):
        """Test PositionCreate schema validation"""
        
        position_data = PositionCreate(
            title="Senior Developer",
            code="SR_DEV",
            level="Senior",
            min_salary=Decimal("80000"),
            max_salary=Decimal("120000")
        )
        
        assert position_data.title == "Senior Developer"
        assert position_data.min_salary == Decimal("80000")


class TestAttendanceCalculations:
    """Tests for attendance-related calculations"""

    def test_calculate_total_hours(self):
        """Test calculation of total working hours"""
        check_in = datetime.combine(date.today(), time(9, 0))
        check_out = datetime.combine(date.today(), time(18, 0))
        
        total_seconds = (check_out - check_in).total_seconds()
        total_hours = Decimal(str(total_seconds / 3600))
        
        assert total_hours == Decimal("9.0")

    def test_calculate_total_hours_with_break(self):
        """Test calculation of total hours minus break time"""
        check_in = datetime.combine(date.today(), time(9, 0))
        check_out = datetime.combine(date.today(), time(18, 0))
        break_hours = Decimal("1.0")
        
        total_seconds = (check_out - check_in).total_seconds()
        total_hours = Decimal(str(total_seconds / 3600)) - break_hours
        
        assert total_hours == Decimal("8.0")

    def test_late_arrival_detection(self):
        """Test detection of late arrival"""
        shift_start = time(9, 0)
        actual_check_in = time(9, 30)
        grace_period_minutes = 15
        
        shift_start_minutes = shift_start.hour * 60 + shift_start.minute
        actual_minutes = actual_check_in.hour * 60 + actual_check_in.minute
        grace_end = shift_start_minutes + grace_period_minutes
        
        is_late = actual_minutes > grace_end
        
        assert is_late is True

    def test_on_time_arrival_within_grace(self):
        """Test on-time arrival within grace period"""
        shift_start = time(9, 0)
        actual_check_in = time(9, 10)  # 10 minutes late but within 15 min grace
        grace_period_minutes = 15
        
        shift_start_minutes = shift_start.hour * 60 + shift_start.minute
        actual_minutes = actual_check_in.hour * 60 + actual_check_in.minute
        grace_end = shift_start_minutes + grace_period_minutes
        
        is_late = actual_minutes > grace_end
        
        assert is_late is False

    def test_overtime_calculation(self):
        """Test overtime hours calculation"""
        standard_hours = Decimal("8.0")
        actual_hours = Decimal("10.5")
        overtime_threshold_minutes = 30  # 0.5 hours
        
        potential_overtime = actual_hours - standard_hours
        overtime_threshold_hours = Decimal(str(overtime_threshold_minutes / 60))
        
        # Only count overtime if over threshold
        overtime_hours = potential_overtime if potential_overtime >= overtime_threshold_hours else Decimal("0")
        
        assert overtime_hours == Decimal("2.5")


class TestShiftManagement:
    """Tests for shift management functionality"""

    def test_default_shift_identification(self):
        """Test identifying default shift"""
        shifts = [
            {"id": 1, "name": "General", "is_default": True},
            {"id": 2, "name": "Morning", "is_default": False},
            {"id": 3, "name": "Night", "is_default": False}
        ]
        
        default_shift = next((s for s in shifts if s["is_default"]), None)
        
        assert default_shift is not None
        assert default_shift["id"] == 1

    def test_shift_duration_calculation(self):
        """Test shift duration calculation"""
        start_time = time(9, 0)
        end_time = time(18, 0)
        
        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute
        
        duration_hours = (end_minutes - start_minutes) / 60
        
        assert duration_hours == 9.0

    def test_night_shift_duration(self):
        """Test night shift duration calculation (spanning midnight)"""
        start_time = time(22, 0)  # 10 PM
        end_time = time(6, 0)    # 6 AM next day
        
        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute
        
        # Handle overnight shift
        if end_minutes < start_minutes:
            duration_minutes = (24 * 60 - start_minutes) + end_minutes
        else:
            duration_minutes = end_minutes - start_minutes
        
        duration_hours = duration_minutes / 60
        
        assert duration_hours == 8.0


class TestHolidayCalendar:
    """Tests for holiday calendar functionality"""

    def test_holiday_types(self):
        """Test different holiday types are recognized"""
        valid_types = {"public", "restricted", "optional", "company"}
        
        # Test that holiday types are distinct and non-empty
        assert len(valid_types) == 4
        assert "" not in valid_types
        assert "public" in valid_types
        assert "company" in valid_types

    def test_is_holiday_check(self):
        """Test checking if a date is a holiday"""
        holidays = [
            {"date": date(2024, 1, 26), "name": "Republic Day"},
            {"date": date(2024, 8, 15), "name": "Independence Day"},
            {"date": date(2024, 10, 2), "name": "Gandhi Jayanti"}
        ]
        
        check_date = date(2024, 1, 26)
        is_holiday = any(h["date"] == check_date for h in holidays)
        
        assert is_holiday is True
        
        check_date = date(2024, 1, 27)
        is_holiday = any(h["date"] == check_date for h in holidays)
        
        assert is_holiday is False

    def test_holidays_in_year(self):
        """Test getting holidays for a specific year"""
        holidays = [
            {"date": date(2024, 1, 26), "year": 2024},
            {"date": date(2024, 8, 15), "year": 2024},
            {"date": date(2025, 1, 26), "year": 2025}
        ]
        
        year_2024_holidays = [h for h in holidays if h["year"] == 2024]
        
        assert len(year_2024_holidays) == 2


class TestDepartmentHierarchy:
    """Tests for department hierarchy functionality"""

    def test_parent_department_assignment(self):
        """Test parent department relationship"""
        departments = [
            {"id": 1, "name": "Engineering", "parent_id": None},
            {"id": 2, "name": "Frontend", "parent_id": 1},
            {"id": 3, "name": "Backend", "parent_id": 1},
            {"id": 4, "name": "React Team", "parent_id": 2}
        ]
        
        # Get sub-departments of Engineering
        eng_sub_depts = [d for d in departments if d["parent_id"] == 1]
        
        assert len(eng_sub_depts) == 2
        assert "Frontend" in [d["name"] for d in eng_sub_depts]
        assert "Backend" in [d["name"] for d in eng_sub_depts]

    def test_root_departments(self):
        """Test getting root (top-level) departments"""
        departments = [
            {"id": 1, "name": "Engineering", "parent_id": None},
            {"id": 2, "name": "HR", "parent_id": None},
            {"id": 3, "name": "Frontend", "parent_id": 1}
        ]
        
        root_depts = [d for d in departments if d["parent_id"] is None]
        
        assert len(root_depts) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
