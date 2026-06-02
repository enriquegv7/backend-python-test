from typing import Optional


class NotificationStore:

    # inicializa el diccionario
    def __init__(self):
        self._store = {}

    # crea una nueva notificacion
    def create(self, id: str, payload: dict) -> dict:
        record = {
            "id": id,
            "status": "queued",
            "payload": payload
        }

        self._store[id] = record
        return record


    # Busca una notifiacion por ID
    def get(self, id: str) -> Optional[dict]:
        return self._store.get(id)

    
    # actualiza el estado de una notificacion
    def update_status(self, id: str, status: str) -> None:
        if id in self._store:
            self._store[id]["status"] = status

    
    # verifica si existe una notificacion
    def exists(self, id: str) -> bool:
        return id in self._store

    

store = NotificationStore()





