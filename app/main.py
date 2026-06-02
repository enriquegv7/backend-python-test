from fastapi import FastAPI
from endpoints.requests import router


app = FastAPI(title="Notification Service (Technical Test)")

app.include_router(router)

