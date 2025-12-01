import uvicorn
from brain_api.core.config import settings

if __name__ == "__main__":

    reload = settings.RELOAD and settings.is_development
    workers = 1 if reload else settings.WORKERS

    uvicorn.run(
        "brain_api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=reload,
        workers=workers,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.is_development,
    )
