from fastapi import FastAPI

app = FastAPI(title="F1 Prediction Model API")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
