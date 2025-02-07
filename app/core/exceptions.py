from fastapi import HTTPException, status


class AuthenticationException(HTTPException):
    def __init__(self, detail=None):
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail)


class DuplicateException(HTTPException):
    def __init__(self, detail="Object already exists"):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail)


class NotAvailableException(HTTPException):
    def __init__(self, detail="Resource is not available"):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail)


class NotFoundException(HTTPException):
    def __init__(self, detail=None):
        super().__init__(status.HTTP_404_NOT_FOUND, detail)


class ValidationException(HTTPException):
    def __init__(self, detail="Cannot save object"):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail)
