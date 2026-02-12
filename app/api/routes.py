from fastapi import APIRouter, Body
from app.services.orchestrator import run_orchestration
from app.memory.store import get_history
from app.memory.feedback import save_feedback
from app.services.orchestrator import get_insights
from fastapi.concurrency import run_in_threadpool

router = APIRouter()

@router.post("/orchestrator/decide")
async def decide(data: dict = Body(...)):
    result = await run_in_threadpool(run_orchestration, data)
    return result


@router.get("/orchestrator/history/{product_id}")
async def history(product_id: str):
    return {
        "product_id": product_id,
        "history": get_history(product_id)
    }

@router.post("/orchestrator/feedback")
async def feedback(data: dict = Body(...)):
    product_id = data.get("product_id")

    if product_id:
        save_feedback(product_id, data)

    return {"status": "feedback recorded"}

@router.get("/orchestrator/insights")
async def insights():
    return get_insights()
