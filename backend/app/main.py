from fastapi import FastAPI

app = FastAPI(
    title="F1 Insight AI",
    description="F1 news collection, LLM summarization & translation API",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
