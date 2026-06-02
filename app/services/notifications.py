import asyncio
from core.store import store
from services.provider import call_provider

# lanza proceso en background
async def process_notification(id: str, payload: dict) -> None:
    store.update_status(id, "processing")
    try:
        await call_provider(payload)
        store.update_status(id, "sent")
    except Exception as e:
        store.update_status(id, "failed")

# Procesa notificaciones
def launch_notification(id: str, payload: dict) -> None:
    asyncio.create_task(process_notification(id, payload))
