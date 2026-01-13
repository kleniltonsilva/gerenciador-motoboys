"""
Database Session Manager - Super Food SaaS
Gerencia conexões e sessões do SQLAlchemy
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv

from .base import Base

# Carrega variáveis de ambiente
load_dotenv()

# URL do banco de dados (SQLite para dev, PostgreSQL para prod)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database/super_food.db")

# Configurações do engine
if "sqlite" in DATABASE_URL:
    # SQLite: usar StaticPool e check_same_thread=False
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Mude para True para ver SQL no console
    )
else:
    # PostgreSQL: configuração padrão
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Testa conexão antes de usar
        echo=False
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Inicializa o banco de dados criando todas as tabelas
    Deve ser chamado no início do app
    """
    Base.metadata.create_all(bind=engine)
    print(f"✅ Banco de dados inicializado: {DATABASE_URL}")


def get_db():
    """
    Dependency para injeção de sessão
    Uso: db = next(get_db())
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """
    Retorna uma sessão direta (sem generator)
    Uso: db = get_db_session()
    IMPORTANTE: Lembre de chamar db.close() depois!
    """
    return SessionLocal()


# ==================== FUNÇÕES AUXILIARES ====================

def criar_super_admin_padrao():
    """Cria super admin padrão se não existir"""
    from .models import SuperAdmin
    
    db = get_db_session()
    try:
        # Verificar se já existe
        admin = db.query(SuperAdmin).filter(
            SuperAdmin.usuario == os.getenv("SUPER_ADMIN_USER", "superadmin")
        ).first()
        
        if not admin:
            admin = SuperAdmin(
                usuario=os.getenv("SUPER_ADMIN_USER", "superadmin"),
                email="admin@superfood.com.br",
                ativo=True
            )
            admin.set_senha(os.getenv("SUPER_ADMIN_PASS", "SuperFood2025!"))
            
            db.add(admin)
            db.commit()
            print("✅ Super Admin padrão criado")
        else:
            print("ℹ️ Super Admin já existe")
            
    except Exception as e:
        print(f"❌ Erro ao criar super admin: {e}")
        db.rollback()
    finally:
        db.close()


def criar_config_padrao_restaurante(restaurante_id: int):
    """Cria configuração padrão para um restaurante"""
    from .models import ConfigRestaurante
    
    db = get_db_session()
    try:
        # Verificar se já existe
        config = db.query(ConfigRestaurante).filter(
            ConfigRestaurante.restaurante_id == restaurante_id
        ).first()
        
        if not config:
            config = ConfigRestaurante(
                restaurante_id=restaurante_id,
                status_atual='fechado',
                modo_despacho='auto_economico',
                taxa_diaria=50.0,
                valor_lanche=15.0,
                taxa_entrega_base=5.0,
                distancia_base_km=3.0,
                taxa_km_extra=1.5,
                valor_km=2.0,
                horario_abertura='18:00',
                horario_fechamento='23:00',
                dias_semana_abertos='segunda,terca,quarta,quinta,sexta,sabado,domingo'
            )
            
            db.add(config)
            db.commit()
            print(f"✅ Config criada para restaurante {restaurante_id}")
            
    except Exception as e:
        print(f"❌ Erro ao criar config: {e}")
        db.rollback()
    finally:
        db.close()