from pydantic import BaseModel


class ConfigOverride(BaseModel):
    crm: str
    batch_size: int
    flush_interval: int
    rate_limit_per_minute: int
