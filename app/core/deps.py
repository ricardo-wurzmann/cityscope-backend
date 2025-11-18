from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import jwt

from core.config import settings
from db.session import get_db
from sqlalchemy.orm import Session
from models.user import User

auth_scheme = HTTPBearer(auto_error=True)


def get_current_user(token=Depends(auth_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        email = payload.get("sub")
        if not email:
            raise ValueError
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
    return user


