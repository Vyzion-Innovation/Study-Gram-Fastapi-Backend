from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileOut
from app.models.profile import Profile
from app.models.user import User

router = APIRouter()

# @router.post("/profile", response_model=ProfileOut)
# def create_profile(
#     profile_data: ProfileCreate = Depends(ProfileCreate.as_form),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     existing = db.query(Profile).filter(Profile.user_id == current_user.id).first()
#     if existing:
#         raise HTTPException(status_code=400, detail="Profile already exists")
#
#     profile = Profile(**profile_data.dict(), user_id=current_user.id)
#     db.add(profile)
#     db.commit()
#     db.refresh(profile)
#     return profile


@router.get("/profile", response_model=ProfileOut)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = (
        db.query(Profile)
        .filter(Profile.user_id == current_user.id)
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile


@router.put("/profile", response_model=ProfileOut)
def update_profile(
    profile_data: ProfileUpdate = Depends(ProfileUpdate.as_form),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Exclude fields you don't want to update
    excluded_fields = {"name", "email", "role", "user_id"}

    for field, value in profile_data.dict(exclude_unset=True).items():
        if field not in excluded_fields and value is not None:
            setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return profile  # ✅ Returns the updated profile as response

