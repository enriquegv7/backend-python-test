import logging
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
from core.config import ( PROVIDER_URL, PROVIDER_HEADERS, MAX_RETRIES, RETRY_MULTIPLIER, RETRY_MIN, RETRY_MAX, TIMEOUT)


logger = logging.getLogger(__name__)


#Llamada a Provider y reintentos
def reintenta_call_provider(excepcion):
    if isinstance(excepcion, httpx.HTTPStatusError):
        return excepcion.response.status_code in (429, 500)
    if isinstance(excepcion, (httpx.ConnectError, httpx.TimeoutException)):
        return True
    return False


@retry(
    retry=retry_if_exception(reintenta_call_provider),
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(RETRY_MULTIPLIER, RETRY_MIN, RETRY_MAX),
    reraise=True
)
async def call_provider(payload):
    logger.info(f"Enviando notificación a {payload.get('to')} via {payload.get('type')}")
    async with httpx.AsyncClient(TIMEOUT) as client:
        response = await client.post(PROVIDER_URL, json=payload, headers=PROVIDER_HEADERS)
        response.raise_for_status()
        logger.info("Notificación enviada correctamente")
        return response.json()


