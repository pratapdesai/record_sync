from pydantic import BaseModel

class Record(BaseModel):
    id: str
    operation: str
    data: dict
    crm: str
    status: str
