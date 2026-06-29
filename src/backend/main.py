from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html

from src.backend.api import routers
from src.backend.core.config import settings
from src.backend.core.database import MongoDB
from src.backend.utils.logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await MongoDB.connect()
    yield
    await MongoDB.close()


app = FastAPI(
    title=settings.project_name,
    version="1.0.0",
    description="Self-healing Kubernetes system with AI-powered diagnostics",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if hasattr(settings, "cors_origins") else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in routers:
    app.include_router(router)


@app.get("/docs", include_in_schema=False)
async def swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{settings.project_name} - API Docs",
    )


@app.get("/openapi.json", include_in_schema=False)
async def openapi():
    return app.openapi()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
