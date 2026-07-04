import uvicorn

from src.core.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
