from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from db.session import get_db
from crud.crud_user import user_crud
from core.config import settings
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")


def get_current_user(
        db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        telegram_id: str = payload.get("sub")
        if telegram_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = user_crud.get_by_telegram_id(db, telegram_id=telegram_id)
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
        current_user: User = Depends(get_current_user),
) -> User:
    """Get current active authenticated user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user