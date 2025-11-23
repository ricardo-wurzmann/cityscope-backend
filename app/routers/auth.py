from fastapi import APIRouter, Depends, Response, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginIn, SignUpIn, TokenOut
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.models.user import User
from app.core.config import settings
import os


router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE_NAME = "cityscope_refresh"

# na função set_refresh_cookie(...)
def set_refresh_cookie(resp: Response, token: str):
    is_dev = os.getenv("DEV_INSECURE_COOKIES", "0") == "1"
    resp.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=not is_dev,          # <- em dev, permite cookie sem Secure
        samesite="lax" if is_dev else "none",
        domain=settings.COOKIE_DOMAIN,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/auth",
    )


@router.post("/signup", response_model=TokenOut)
def signup(payload: SignUpIn, response: Response, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    access = create_access_token(user.email)
    refresh = create_refresh_token(user.email)
    set_refresh_cookie(response, refresh)
    return TokenOut(access_token=access)


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token(user.email)
    refresh = create_refresh_token(user.email)
    set_refresh_cookie(response, refresh)
    return TokenOut(access_token=access)


@router.post("/refresh", response_model=TokenOut)
def refresh_token(request: Request):
    token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    import jwt

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        sub = payload.get("sub")
        if not sub:
            raise ValueError
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access = create_access_token(sub)
    return TokenOut(access_token=access)


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(REFRESH_COOKIE_NAME, path="/auth", domain=settings.COOKIE_DOMAIN)
    return {"ok": True}


