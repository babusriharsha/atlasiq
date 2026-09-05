from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="AtlasIQ",
    description="Enterprise AI Knowledge Assistant",
    version="0.1.0",
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "application": "AtlasIQ",
        "status": "running",
    }
