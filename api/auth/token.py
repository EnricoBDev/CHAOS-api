import logging
from datetime import datetime, timedelta

import jwt
from jwt import InvalidTokenError
from pydantic import BaseModel

from globals.constants import ALGORITHM, JWT_EXP_DAYS, SECRET
from globals.exceptions import InvalidTokenException

logger = logging.getLogger("uvicorn.error")


class Token(BaseModel):
    access_token: str
    token_type: str


def create_access_token(data: dict) -> Token:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=JWT_EXP_DAYS)
    logger.info(f"Expire timestamp: {expire}")
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
    return Token(access_token=encoded_jwt, token_type="bearer")


def get_id_from_token(token: str) -> int:
    try:
        payload: dict = jwt.decode(token, SECRET, algorithms=ALGORITHM)
    except InvalidTokenError:
        raise InvalidTokenException()

    if payload.get("sub") is None:
        raise InvalidTokenException()

    id: int = int(payload.get("sub").split(":")[1])

    return id
