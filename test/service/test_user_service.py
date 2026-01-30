import pytest
from sqlmodel import Session, select

from auth.token import create_access_token
from globals.constants import INITIAL_POINTS
from globals.exceptions import InvalidTokenException, UniqueViolationException
from mappers import user_mapper
from models import User, UserCreate
from service.user_service import create_new_user, get_current_user, get_user_by_id


def test_create_new_user(mock_session_db: Session):
    user_create = UserCreate(email="test@test.com", username="test", password="test")

    create_new_user(user=user_create, session=mock_session_db)

    # new User will have id=3
    db_user = mock_session_db.exec(select(User).where(User.id == 3)).one()

    # cannot test for equality between two User objects since we would need to calculate the password hash

    assert db_user.id == 3 and db_user.transactions[0].amount == INITIAL_POINTS


def test_create_new_user_integrity_violation(mock_session_db: Session):
    user_create = UserCreate(
        email="gambler@mail.com", username="gambler", password="test"
    )

    with pytest.raises(UniqueViolationException):
        create_new_user(user_create, mock_session_db)


def test_get_user_by_id(mock_session_db: Session):
    user = User(id=67, username="test", email="test@test.it", password="password")
    mock_session_db.add(user)

    actual = get_user_by_id(id=67, session=mock_session_db)
    expected = user_mapper.user_to_public(user=user, session=mock_session_db)

    assert actual == expected


def test_user_not_found(mock_session_db: Session):
    id = 60
    user = get_user_by_id(id=id, session=mock_session_db)
    assert user is None


def test_get_current_user(mock_session_db: Session):
    user = User(
        id=3,
        username="test_user",
        email="test@test.it",
        password="password",
        transactions=[],
        created_events=[],
    )
    public_user = user_mapper.user_to_public(user=user, session=mock_session_db)
    mock_session_db.add(user)
    mock_session_db.commit()

    payload = {"sub": f"user:{user.id}"}
    token = create_access_token(payload)

    current_user = get_current_user(mock_session_db, token.access_token)

    assert current_user is not None
    assert current_user == public_user


def test_get_current_user_invalid_token(mock_session_db: Session):
    with pytest.raises(InvalidTokenException):
        get_current_user(mock_session_db, "invalid_token")
