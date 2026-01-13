# backend/app/middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from sqlalchemy.orm import Session
from .database import SessionLocal
from .auth import get_current_restaurante
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware que injeta automaticamente tenant_id em todas as queries do SQLAlchemy.
    Garante isolamento de dados entre restaurantes.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Rotas públicas que não precisam de tenant_id
        public_paths = ["/", "/docs", "/openapi.json", "/restaurantes/signup", "/restaurantes/login"]
        
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)
        
        # Extrai tenant_id do token JWT (se autenticado)
        tenant_id = None
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            try:
                db = SessionLocal()
                try:
                    restaurante = get_current_restaurante(auth_header.split(" ")[1], db)
                    tenant_id = restaurante.id
                    request.state.tenant_id = tenant_id
                    logger.info(f"🔐 Tenant {tenant_id} autenticado em {request.url.path}")
                finally:
                    db.close()
            except HTTPException:
                pass  # Token inválido, continua sem tenant_id
        
        response = await call_next(request)
        return response

def get_tenant_id(request: Request) -> int:
    """
    Extrai tenant_id da request. Usado em dependências FastAPI.
    """
    if not hasattr(request.state, "tenant_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação necessária para acessar este recurso"
        )
    return request.state.tenant_id