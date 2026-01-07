from fastapi import FastAPI

app = FastAPI(title="Job Hunter Agent API")

@app.get("/health")
def health():
    return {"ok": True}
