from fastapi import HTTPException, status


def http_unauthorized_exception(message: str):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )


def http_conflict_exception(message: str):
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)


def http_not_found_exception(message: str):
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)


def http_forbidden_exception(message: str):
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)


class InvalidTokenException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class UniqueViolationException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class ForbiddenOperationException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class NotFoundException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class FKIntegrityViolationException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class TimezoneValidationException(Exception):
    def __init__(self, *args):
        super().__init__(*args)
