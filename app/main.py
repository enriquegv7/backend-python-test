import httpx
import uuid
import asyncio 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception


app = FastAPI(title="Notification Service (Technical Test)")

PROVIDER_URL = "http://localhost:3001/v1/notify"
PROVIDER_HEADERS = {
    "X-API-Key": "test-dev-2026",
    "Content-Type": "application/json"
}


requests_db = {}


# Modelos necesarios
# Modelo Registro de Solicitud
class NotificationRequest(BaseModel):
    to: str
    message: str
    type: Literal["email", "sms", "push"]

class NotificationResponse(BaseModel):
    id: str

# Modelo Consulta de Estado
class StatusResponse(BaseModel):
    id: str
    status: Literal["queued", "processing", "sent", "failed"]



#Llamada a Provider y reintentos

def reintenta_call_provider(excepcion):
    if isinstance(excepcion, httpx.HTTPStatusError):
        return excepcion.response.status_code in (429, 500)
    if isinstance(excepcion, (httpx.ConnectError, httpx.TimeoutException)):
        return True
    return False


@retry(
    retry=retry_if_exception(reintenta_call_provider),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=0.3, min=0.3, max=2.4),
    reraise=True
)
async def call_provider(payload):
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(PROVIDER_URL, json=payload, headers=PROVIDER_HEADERS)
        response.raise_for_status()
        return response.json()




# 1º endpoint
@app.post("/v1/requests", status_code=201, response_model = NotificationResponse)
async def crear_solicitud(notificacion: NotificationRequest):
    id = str(uuid.uuid4())
    requests_db[id] = {
        "id": id,
        "status": "queued",
        "payload": notificacion.model_dump()
    }
    return {"id": id}


# 2º endpoint 
# funcion auxiliar que actualiza el estado
async def process_notification(id, payload):
    requests_db[id]["status"] = "processing"
    try:
        await call_provider(payload)
        requests_db[id]["status"] = "sent"
    except Exception:
        requests_db[id]["status"] = "failed"


@app.post("/v1/requests/{id}/process", status_code = 202)
async def procesar_solicitud(id):
    if id not in requests_db:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    if requests_db[id]["status"] in ("processing", "sent"):
        return {"message": "La solicitud ya está siendo procesada o fue enviada"}

    asyncio.create_task(process_notification(id, requests_db[id]["payload"]))
    return {"message": "Procesamiento iniciado", "id": id}


# 3º endpoint
@app.get("/v1/requests/{id}", response_model = StatusResponse)
async def consultar_estado(id):
    if id not in requests_db:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    return requests_db[id]


