import logging

from fastapi import APIRouter, HTTPException

from server.models import (
    MemoryForgetRequest,
    MemoryForgetResponse,
    MemoryGetRequest,
    MemoryGetResponse,
    MemorySearchRequest,
    MemorySearchResponse,
    MemorySetRequest,
    MemorySetResponse,
)
from server.services.memory_service import (
    memory_forget,
    memory_get,
    memory_search,
    memory_set,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/memory", tags=["memory"])


@router.post("/set", response_model=MemorySetResponse)
async def set_memory(req: MemorySetRequest):
    try:
        key = await memory_set(
            key=req.key,
            value=req.value,
            scope=req.scope,
            tags=req.tags,
            tags_search=req.tags_search,
            expiration_days=req.expiration_days,
        )
        return MemorySetResponse(status="ok", key=key)
    except Exception as e:
        logger.exception("memory_set failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get", response_model=MemoryGetResponse)
async def get_memory(req: MemoryGetRequest):
    try:
        item = await memory_get(req.key)
        if item:
            return MemoryGetResponse(status="ok", memory=item)
        return MemoryGetResponse(status="not_found")
    except Exception as e:
        logger.exception("memory_get failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=MemorySearchResponse)
async def search_memory(req: MemorySearchRequest):
    try:
        results = await memory_search(
            query=req.query,
            scope=req.scope,
            limit=req.limit,
        )
        return MemorySearchResponse(status="ok", results=results)
    except Exception as e:
        logger.exception("memory_search failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forget", response_model=MemoryForgetResponse)
async def forget_memory(req: MemoryForgetRequest):
    try:
        deleted = await memory_forget(req.key)
        status = "ok" if deleted else "not_found"
        return MemoryForgetResponse(status=status, key=req.key)
    except Exception as e:
        logger.exception("memory_forget failed")
        raise HTTPException(status_code=500, detail=str(e))
