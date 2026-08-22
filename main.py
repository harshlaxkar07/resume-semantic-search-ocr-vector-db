from fastapi import FastAPI

from app.logger import logger
from routers.resume import router as resume_router
from routers.search import router as search_router


def create_application() -> FastAPI:

    logger.info("Starting Resume Vector Database API...")

    application = FastAPI(
        title="Resume Vector Database",
        version="1.0.0",
    )

    application.include_router(resume_router)
    application.include_router(search_router)

    logger.success("Application started successfully.")

    return application


app = create_application()