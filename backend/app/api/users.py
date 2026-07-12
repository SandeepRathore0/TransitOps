from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Role
from app.schemas.user_schemas import UserCreate, UserResponse, RoleResponse
from app.middleware.rbac import RoleChecker
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
allow_admin = RoleChecker(["Admin"])

@router.get("/roles", response_model=list[RoleResponse], dependencies=[Depends(allow_admin)])
def get_roles(db: Session = Depends(get_db)):
    # Auto-seed roles if missing
    roles_list = ["Admin", "Fleet Manager", "Dispatcher", "Safety Officer", "Financial Analyst"]
    for r in roles_list:
        if not db.query(Role).filter(Role.name == r).first():
            db.add(Role(name=r))
    db.commit()
    return db.query(Role).all()

@router.get("/", response_model=list[UserResponse], dependencies=[Depends(allow_admin)])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).filter(User.deleted_at == None).all()

@router.post("/", response_model=UserResponse, dependencies=[Depends(allow_admin)])
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check email exists
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Get role
    role = db.query(Role).filter(Role.name == user_in.role_name).first()
    if not role:
        raise HTTPException(status_code=400, detail="Invalid role name")
        
    hashed_password = pwd_context.hash(user_in.password)
    
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=hashed_password,
        role_id=role.id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
