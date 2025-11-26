from contextlib import asynccontextmanager

from fastapi import FastAPI

# Import models first to register them with SQLModel.metadata
# (before any routing imports that depend on get_session)
from api.signals.models import SignalModel
from api.conversations.models import ConversationModel, SignalDriftMetricModel
from api.users.models import UserModel
from api.conversations import router as conversation_router
from api.db.session import init_db
from api.signals import router as signal_router
from api.users.routing import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # before app startup up
    init_db()
    yield
    # clean up


app = FastAPI(lifespan=lifespan)
app.include_router(signal_router, prefix="/api/signals")
app.include_router(conversation_router, prefix="/api/conversations")
app.include_router(user_router, prefix="/api/users")


@app.get("/healthz")
def read_api_health():
    """Health check endpoint"""
    return {"status": "ok"}
