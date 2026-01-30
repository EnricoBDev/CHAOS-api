from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
OAuth2Dep = Annotated[str, Depends(_oauth2_scheme)]
