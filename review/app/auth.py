from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException


@dataclass
class User:
    id: str
    roles: set[str]


def get_current_user(authorization: str = Header(...)) -> User:
    token = authorization.removeprefix("Bearer ")
    user = _lookup_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


def require_role(role: str):
    def check(user: User = Depends(get_current_user)) -> User:
        if role not in user.roles:
            raise HTTPException(status_code=403, detail="Not allowed")
        return user

    return check


def _lookup_token(token: str) -> User | None:
    raise NotImplementedError("Provided by the platform at deploy time")
