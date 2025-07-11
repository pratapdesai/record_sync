from abc import ABC, abstractmethod
from typing import Dict


class BaseCRM(ABC):

    @classmethod
    @abstractmethod
    def config_schema(cls) -> Dict[str, str]:
        """
        Returns the expected config keys and descriptions.
        """
        pass

    def __init__(self, config):
        self.config = config

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

    async def fetch_recent_changes(self, since_timestamp):
        """
        Optional: Implement this in subclasses that support pulling.
        """
        raise NotImplementedError("This CRM does not support polling.")
