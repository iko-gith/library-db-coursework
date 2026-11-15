import bcrypt
from sqlalchemy.orm import Session
from src.models import Base
from sqlalchemy import Column, Integer, String, ForeignKey

class AppUser(Base):
    """Учетная запись пользователя"""
    __tablename__ = 'app_user'

    id            = Column(Integer, primary_key=True, autoincrement=True)
    username      = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role          = Column(String(50), nullable=False)  # 'admin', 'librarian', 'reader'
    employee_id   = Column(Integer, ForeignKey('employee.id', ondelete='CASCADE'), nullable=True)
    reader_id     = Column(Integer, ForeignKey('reader.id', ondelete='CASCADE'), nullable=True)


def hash_password(plain_password: str) -> str:
    """Хэширование пароля"""
    salt   = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка соответствия пароля"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def authenticate_user(session: Session, username: str, plain_password: str) -> Optional[AppUser]:
    """Аутентификация пользователя"""
    user = session.query(AppUser).filter(AppUser.username == username).first()
    
    if not user or not verify_password(plain_password, user.password_hash):
        user = None
        
    return user


def check_permission(user_role: str, required_roles: list) -> bool:
    """Проверка прав доступа"""
    return user_role in required_roles
