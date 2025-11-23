from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, cities, indicators, states

app = FastAPI(title="CityScope API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(cities.router)
app.include_router(indicators.router)
app.include_router(states.router)


@app.get("/healthz")
def healthz():
    return {"ok": True}


