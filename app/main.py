from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from app.database.config import Base, engine
from app.routes import (
    auth, profile, batch, regular_student, pte_student, demo_student, performance,
    mock_test, transaction, visa, teacher, expense, student_attendance, teacher_attendance, dashboard
)

# ✅ Disable default Swagger & Redoc docs
app = FastAPI(docs_url=None, redoc_url=None)

# ✅ Create tables if not exist
Base.metadata.create_all(bind=engine)

# ✅ Include routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(profile.router, tags=["Profile"])
app.include_router(batch.router, tags=["Batch Module"])
app.include_router(regular_student.router)
app.include_router(pte_student.router)
app.include_router(demo_student.router)
app.include_router(performance.router)
app.include_router(mock_test.router)
app.include_router(transaction.router)
app.include_router(visa.router)
app.include_router(teacher.router)
app.include_router(expense.router)
app.include_router(student_attendance.router)
app.include_router(teacher_attendance.router)
app.include_router(dashboard.router)

# ✅ Add pagination support
add_pagination(app)

# ✅ Custom Swagger docs with persistAuthorization
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Studygram API Docs",
        swagger_ui_parameters={"persistAuthorization": True}  # 🔐 <- Keeps token after refresh
    )

# ✅ Optional: custom openapi.json endpoint
@app.get("/openapi.json", include_in_schema=False)
async def custom_openapi():
    return get_openapi(
        title="Studygram API",
        version="1.0.0",
        routes=app.routes
    )
