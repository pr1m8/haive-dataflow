# app/models.py
# Defines request/response models
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    message: str

class MessagePayload(BaseModel):
    message: str
