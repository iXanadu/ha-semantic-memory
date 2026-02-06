from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/escalate", tags=["escalation"])


@router.post("")
async def escalate():
    raise HTTPException(status_code=501, detail="Escalation not yet implemented")
