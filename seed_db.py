import os
import sys

# Add backend directory to sys.path so we can import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app.database import SessionLocal, engine, Base
from app.models.models import Role, User
from app.auth.auth import get_password_hash

# Ensure tables exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    roles = ["Fleet Manager", "Dispatcher", "Safety Officer", "Financial Analyst"]
    for role_name in roles:
        if not db.query(Role).filter(Role.name == role_name).first():
            db.add(Role(name=role_name))
    
    db.commit()
    
    manager_role = db.query(Role).filter(Role.name == "Fleet Manager").first()
    
    if manager_role and not db.query(User).filter(User.email == "admin@transitops.com").first():
        admin = User(
            name="System Admin",
            email="admin@transitops.com",
            password_hash=get_password_hash("password123"),
            role_id=manager_role.id
        )
        db.add(admin)
        db.commit()
        print("Database seeded successfully! Admin created (admin@transitops.com / password123)")
    else:
        print("Database already seeded.")
        
finally:
    db.close()
