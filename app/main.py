from fastapi import FastAPI

app = FastAPI(
    title="AtlasIQ",
    description="Enterprise AI Knowledge Assistant",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "application": "AtlasIQ",
        "status": "running"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
