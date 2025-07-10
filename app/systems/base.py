from abc import ABC, abstractmethod
from typing import List, Dict

class BaseSystem(ABC):
    @abstractmethod
    async def fetch_records(self) -> List[Dict]:
        pass

    @abstractmethod
    async def write_record(self, record: Dict) -> None:
        pass
