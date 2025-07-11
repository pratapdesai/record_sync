from typing import Dict, Type
from app.crms.base import BaseCRM

crm_registry: Dict[str, Type[BaseCRM]] = {}


def register_crm(name: str):
    def wrapper(cls: Type[BaseCRM]):
        crm_registry[name.lower()] = cls
        return cls

    return wrapper
