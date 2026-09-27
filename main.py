from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.logger import logger
from routers.resume import router as resume_router
from routers.search import router as search_router


BASE_DIR = Path(__file__).resolve().parent

FRONTEND_DIR = BASE_DIR / "frontend"


def create_application() -> FastAPI:

    logger.info("Starting Resume Vector Database API...")

    application = FastAPI(
        title="Resume Vector Database",
        version="1.0.0",
        description=(
            "Upload résumés with OCR fallback, embed them into a vector "
            "store, and search the collection by meaning. The search "
            "console is served at /ui."
        ),
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(resume_router)
    application.include_router(search_router)

    @application.get("/health", tags=["Health"])
    def health() -> dict[str, str]:
        """
        Liveness probe for the API.
        """

        return {"status": "healthy"}

    if FRONTEND_DIR.is_dir():

        application.mount(
            "/ui",
            StaticFiles(directory=FRONTEND_DIR, html=True),
            name="ui",
        )

        @application.get("/", include_in_schema=False)
        def console() -> RedirectResponse:
            """
            Send the application root to the search console.
            """

            return RedirectResponse(url="/ui/")

        logger.info("Search console mounted at /ui")

    logger.success("Application started successfully.")

    return application


app = create_application()
