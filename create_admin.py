from app.database.session import SessionLocal
from app.models.user import User
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
    print("✅ Admin user created.")
else:
    print("⚠️ A user with this email already exists.")
