from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from auth import password, token
from globals.constants import INITIAL_POINTS
from globals.exceptions import InvalidTokenException, UniqueViolationException
from mappers import user_mapper
from models import Transaction, User, UserCreate, UserPublic


def create_new_user(user: UserCreate, session: Session):
    table_user = User.model_validate(user)
    plain_password = user.password
    hash_password = password.calculate_hash(plain_password)
    table_user.password = hash_password

    try:
        session.add(table_user)
        session.flush()
        session.refresh(table_user)
    except IntegrityError:
        raise UniqueViolationException("Email or username weren't unique")

    initial_transaction = Transaction(
        description="Initial transaction",
        amount=INITIAL_POINTS,
        timestamp=int(datetime.now().timestamp()),
        user=table_user,
    )

    table_user.transactions = [initial_transaction]
    session.add(table_user)
    session.commit()


def get_user_by_id(id: int, session: Session) -> UserPublic | None:
    table_user = session.exec(select(User).where(User.id == id)).first()

    if table_user is None:
        return None

    public_user = user_mapper.user_to_public(table_user, session)

    return public_user


def get_current_user(session: Session, access_token: str) -> UserPublic | None:
    try:
        id = token.get_id_from_token(access_token)
    except InvalidTokenException:
        raise InvalidTokenException()

    return get_user_by_id(id, session)
