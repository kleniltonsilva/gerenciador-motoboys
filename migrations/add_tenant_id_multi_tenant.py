# migrations/add_tenant_id_multi_tenant.py
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./super_food.db")  # Ajuste se seu .db tiver outro nome

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

print("🔄 Iniciando migration multi-tenant...")

with engine.begin() as conn:
    try:
        # Adiciona tenant_id nas tabelas relevantes
        conn.execute(text("ALTER TABLE pedidos ADD COLUMN tenant_id INTEGER REFERENCES restaurantes(id)"))
        conn.execute(text("ALTER TABLE motoboys ADD COLUMN tenant_id INTEGER REFERENCES restaurantes(id)"))

        # Preenche com o valor existente de restaurante_id
        conn.execute(text("UPDATE pedidos SET tenant_id = restaurante_id WHERE tenant_id IS NULL"))
        conn.execute(text("UPDATE motoboys SET tenant_id = restaurante_id WHERE tenant_id IS NULL"))

        # Índices para performance
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_pedidos_tenant ON pedidos(tenant_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_pedidos_tenant_data ON pedidos(tenant_id, data_criacao)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_motoboys_tenant ON motoboys(tenant_id)"))

        print("✅ Migration multi-tenant concluída com sucesso!")
        print("   Todas as tabelas agora têm isolamento explícito via tenant_id (= restaurante.id)")
    except Exception as e:
        print(f"⚠️ Erro (provavelmente coluna já existe): {e}")
        print("   Pode ignorar se a migration já foi executada antes.")