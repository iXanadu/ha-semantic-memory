from pydantic import BaseModel, field_validator


# --- Request models (match original Pyscript tool interface) ---

class MemorySetRequest(BaseModel):
    key: str
    value: str
    scope: str = "user"
    tags: str = ""
    tags_search: str = ""
    expiration_days: int = 180
    force_new: bool = False

    @field_validator("tags", mode="before")
    @classmethod
    def coerce_tags(cls, v):
        if isinstance(v, list):
            return ", ".join(str(t) for t in v)
        return v


class MemoryGetRequest(BaseModel):
    key: str


class MemorySearchRequest(BaseModel):
    query: str
    scope: str = "user"
    limit: int = 5


class MemoryForgetRequest(BaseModel):
    key: str


# --- Response models ---

class MemoryItem(BaseModel):
    key: str
    value: str
    scope: str
    tags: str
    tags_search: str
    score: float | None = None


class MemorySetResponse(BaseModel):
    status: str
    key: str


class MemoryGetResponse(BaseModel):
    status: str
    memory: MemoryItem | None = None


class MemorySearchResponse(BaseModel):
    status: str
    results: list[MemoryItem]


class MemoryForgetResponse(BaseModel):
    status: str
    key: str
