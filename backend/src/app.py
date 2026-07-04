from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from src.agent.graph import compile_graph
from src.api.routes.health import router as health_router
from src.api.routes.post import router as post_router
from src.core.config import get_settings
from src.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    settings = get_settings()
    Path(settings.checkpoint_db_path).parent.mkdir(parents=True, exist_ok=True)

    async with AsyncSqliteSaver.from_conn_string(settings.checkpoint_db_path) as checkpointer:
        app.state.graph = compile_graph(checkpointer)
        app.state.checkpointer = checkpointer
        yield


app = FastAPI(title="AMA", lifespan=lifespan)
app.include_router(health_router)
app.include_router(post_router)
