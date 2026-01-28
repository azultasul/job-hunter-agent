from fastapi import FastAPI
from contextlib import asynccontextmanager
from pathlib import Path

import dotenv
dotenv.load_dotenv()

from app.routers import crew, steps


@asynccontextmanager
async def lifespan(app: FastAPI):
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    yield


app = FastAPI(title="Job Search Agent API", lifespan=lifespan)

app.include_router(crew.router)
app.include_router(steps.router)
