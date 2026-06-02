from pydantic import BaseModel, field_validator
from typing import Literal


# Modelo Registro de Solicitud
class NotificationRequest(BaseModel):
    to: str
    message: str
    type: Literal["email", "sms", "push"]

    @field_validator("to", "message")
    @classmethod
    def no_vacio(cls, field_value: str) -> str:
        if not field_value or not field_value.strip():
            raise ValueError("El campo no puede estar vacío")
        return field_value.strip()


class NotificationResponse(BaseModel):
    id: str

# Modelo Consulta de Estado
class StatusResponse(BaseModel):
    id: str
    status: Literal["queued", "processing", "sent", "failed"]


