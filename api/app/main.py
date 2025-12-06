import logging

from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from app.config import settings
from routers import users, finance, admin, messages
from services.alfacrm import AlfaCRMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    yield
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency для проверки токена
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> bool:
    if credentials.credentials != settings.backend_api_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid API token"
        )
    return True


# Health check
@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.app_name}"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Подключаем роуты с аутентификацией
app.include_router(
    users.router,
    prefix=settings.api_v1_prefix,
    dependencies=[Depends(verify_token)]
)
app.include_router(
    finance.router,
    prefix=settings.api_v1_prefix,
    dependencies=[Depends(verify_token)]
)
app.include_router(
    admin.router,
    prefix=settings.api_v1_prefix,
    dependencies=[Depends(verify_token)]
)
app.include_router(
    messages.router,
    prefix=settings.api_v1_prefix,
    dependencies=[Depends(verify_token)]
)
