from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, cities, indicators

app = FastAPI(title="CityScope API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(cities.router)
app.include_router(indicators.router)


@app.get("/healthz")
def healthz():
    return {"ok": True}


