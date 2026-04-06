from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import quality

app = FastAPI(
    title="Data Quality API",
    description="API REST pour l'analyse et la validation de la qualité des données",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quality.router, prefix="/api/v1", tags=["quality"])


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "version": "1.0.0"}
