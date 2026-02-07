from fastapi import FastAPI

from app.api.router import router as api_router

app = FastAPI(title="QuantLab Backend")

app.include_router(api_router)
