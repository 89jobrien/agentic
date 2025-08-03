from fastapi import APIRouter

general_router = APIRouter(tags=["General"])


@general_router.get("/", tags=["General"])
def root():
    return {"message": "Welcome to Agentic - RAG codebase analyzer."}


@general_router.get("/health", tags=["General"])
def health():
    return {"status": "ok"}
