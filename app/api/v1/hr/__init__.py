from fastapi import APIRouter

hr_router = APIRouter()

def register_hr_subrouters(hr_router: APIRouter):
    from .hr_core import router as hr_core_router
    hr_router.include_router(hr_core_router)

    from .hr_attendance import router as hr_attendance_router
    hr_router.include_router(hr_attendance_router)

    from .hr_leave import router as hr_leave_router
    hr_router.include_router(hr_leave_router)

    from .hr_performance import router as hr_performance_router
    hr_router.include_router(hr_performance_router)

    from .hr_recruitment import router as hr_recruitment_router
    hr_router.include_router(hr_recruitment_router)

    from .hr_compliance import router as hr_compliance_router
    hr_router.include_router(hr_compliance_router)

    from .hr_advanced import router as hr_advanced_router
    hr_router.include_router(hr_advanced_router)

    from .hr_exports import router as hr_exports_router
    hr_router.include_router(hr_exports_router)

register_hr_subrouters(hr_router)