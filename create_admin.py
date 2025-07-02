from app.database.session import SessionLocal
from app.models.user import User
from app.models.profile import Profile
from app.core.security import get_hashed_password

db = SessionLocal()

name = input("Enter name: ")
email = input("Enter email: ")
password = input("Enter password: ")

existing_user = db.query(User).filter(User.email == email).first()

if not existing_user:
    new_admin = User(
        name=name,
        email=email,
        password=get_hashed_password(password),
        role="admin"
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)  # ✅ Needed to get new_admin.id

    # ✅ Create profile
    new_profile = Profile(
        name=new_admin.name,
        email=new_admin.email,
        role=new_admin.role,
        user_id=new_admin.id
        # other fields will default to "", which is fine
    )
    db.add(new_profile)
    db.commit()

    print("✅ Admin user and profile created.")
else:
    print("⚠️ A user with this email already exists.")
