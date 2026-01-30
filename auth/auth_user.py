from typing import Literal

from sqlmodel import Session, select

from models import User

from .password import verify_password  # type: ignore


def authenticate_user(
    session: Session, username: str, password: str
) -> User | Literal[False]:
    user = session.exec(select(User).where(User.username == username)).first()
    if user is not None:
        if not verify_password(password, user.password):
            return False

        return user

    return False
