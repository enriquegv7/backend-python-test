import uuid
import logging
from fastapi import APIRouter, HTTPException
from core.store import store
from models.schemas import NotificationRequest, NotificationResponse, StatusResponse
from services.notifications import launch_notification


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/requests")


# 1º endpoint
@router.post("", status_code=201, response_model=NotificationResponse)
async def crear_solicitud(notificacion: NotificationRequest):
    id = str(uuid.uuid4())
    store.create(id, notificacion.model_dump())
    return {"id": id}


# 2º endpoint 
@router.post("/{id}/process", status_code=202)
async def procesar_solicitud(id: str):
    if not store.exists(id):
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    record = store.get(id)

    if record["status"] in ("processing", "sent"):
        return {"message": "La solicitud ya está siendo procesada o fue enviada"}

    if record["status"] == "failed":
        store.update_status(id, "queued")
        logger.info(f"Reintentando solicitud fallida {id}")

    launch_notification(id, record["payload"])
    return {"message": "Procesamiento iniciado", "id": id}


# 3º endpoint
@router.get("/{id}", response_model=StatusResponse)
async def consultar_estado(id: str):
    if not store.exists(id):
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    return store.get(id)


