from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import benefits, nudges, transactions


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dev-only convenience: creates tables if they don't exist yet.
    # Once the team is stable, switch to Alembic migrations instead.
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Benefit Underutilization Analytics API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server (Vite default)
    allow_origin_regex=r"https://.*\.vercel\.app",  # covers prod + every Vercel preview URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


app.include_router(benefits.router)
app.include_router(transactions.router)
app.include_router(nudges.router)