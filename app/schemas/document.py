from pydantic import BaseModel


class DocumentCreate(BaseModel):
    filename: str
    file_type: str
    team: str
    storage_path: str

class DocumentUpdate(BaseModel):
    filename: str
    file_type: str
    team: str
    storage_path: str
