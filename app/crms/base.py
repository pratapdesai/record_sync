from abc import ABC, abstractmethod
from jose import jwt


class BaseCRM(ABC):
    @abstractmethod
    async def push(self, data: dict):
        pass

    @abstractmethod
    def transform(self, data: dict) -> dict:
        pass

    @abstractmethod
    def identify(self) -> str:
        pass

    def _get_jwt_token(self) -> str:
        return "mocked-jwt-token"
        # return jwt.encode({"iss": "record_sync"}, self.secret, algorithm="HS256")
