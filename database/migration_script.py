"""
Migration Script - Super Food SaaS
Migra dados do SQLite antigo (super_food.db) para nova estrutura SQLAlchemy
"""

import sqlite3
import sys
import os
from datetime import datetime, timedelta

# Adicionar path do projeto
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.session import (
    init_db,
    get_db_session,
    criar_super_admin_padrao,
    criar_config_padrao_restaurante
)
from database.models import Restaurante, Motoboy, Pedido


def parse_datetime(value):
    """Converte string de data aceitando com ou sem microssegundos"""
    if not value:
        return None

    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass

    return None


def normalize_unique(value):
    """
    Normaliza campos UNIQUE:
    ''  -> None
    '   ' -> None
    """
    if value is None:
        return None
    value = str(value).strip()
    return value if value else None


def conectar_banco_antigo():
    db_path = os.path.join(
        os.path.dirname(__file__),
        "../streamlit_app/super_food.db"
    )

    if not os.path.exists(db_path):
        print("ℹ️ Banco antigo não encontrado, pulando migração")
        return None

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def migrar_restaurantes(conn_antigo, db_novo):
    print("\n📤 Migrando restaurantes...")

    cursor = conn_antigo.cursor()
    cursor.execute("SELECT * FROM restaurantes")
    restaurantes = cursor.fetchall()

    count = 0

    for r in restaurantes:
        r = dict(r)

        try:
            existe = db_novo.query(Restaurante).filter(
                Restaurante.email == r["email"]
            ).first()

            if existe:
                print(f"  ⏭️ {r['email']} já existe, pulando")
                continue

            restaurante = Restaurante(
                nome=r.get("nome_fantasia") or r.get("nome") or "Restaurante",
                nome_fantasia=r.get("nome_fantasia") or r.get("nome") or "Restaurante",
                razao_social=r.get("razao_social"),
                cnpj=normalize_unique(r.get("cnpj")),
                email=r["email"],
                senha=r["senha_hash"],
                telefone=r.get("telefone"),
                endereco_completo=r.get("endereco_completo"),
                plano=r.get("plano", "basico"),
                valor_plano=r.get("valor_plano", 199.0),
                limite_motoboys=r.get("limite_motoboys", 3),
                codigo_acesso="",
                ativo=r.get("status", "ativo") == "ativo",
                status=r.get("status", "ativo"),
                criado_em=parse_datetime(r.get("data_criacao")) or datetime.utcnow(),
                data_vencimento=parse_datetime(r.get("data_vencimento"))
                or datetime.utcnow() + timedelta(days=30),
            )

            restaurante.gerar_codigo_acesso()

            db_novo.add(restaurante)
            db_novo.flush()

            criar_config_padrao_restaurante(restaurante.id)

            count += 1
            print(f"  ✅ Migrado: {restaurante.nome_fantasia} (ID {restaurante.id})")

        except Exception as e:
            db_novo.rollback()
            print(f"  ❌ Erro ao migrar {r.get('email')}: {e}")

    db_novo.commit()
    print(f"\n✅ {count} restaurantes migrados")
    return count


def migrar_motoboys(conn_antigo, db_novo):
    print("\n📤 Migrando motoboys...")

    cursor = conn_antigo.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='motoboys'"
    )

    if not cursor.fetchone():
        print("  ℹ️ Tabela motoboys não existe")
        return 0

    cursor.execute("SELECT * FROM motoboys")
    motoboys = cursor.fetchall()

    count = 0

    for m in motoboys:
        m = dict(m)

        try:
            if not m.get("restaurante_id"):
                continue

            motoboy = Motoboy(
                restaurante_id=m["restaurante_id"],
                nome=m["nome"],
                usuario=m.get("usuario") or m["nome"].lower().replace(" ", ""),
                telefone=m.get("telefone"),
                senha=m.get("senha"),
                status=m.get("status", "ativo"),
                total_entregas=m.get("total_entregas", 0),
                total_ganhos=m.get("total_ganhos", 0.0),
                data_cadastro=parse_datetime(m.get("data_cadastro")) or datetime.utcnow(),
            )

            db_novo.add(motoboy)
            count += 1

        except Exception as e:
            db_novo.rollback()
            print(f"  ❌ Erro motoboy {m.get('nome')}: {e}")

    db_novo.commit()
    print(f"✅ {count} motoboys migrados")
    return count


def migrar_pedidos(conn_antigo, db_novo):
    print("\n📤 Migrando pedidos...")

    cursor = conn_antigo.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='pedidos'"
    )

    if not cursor.fetchone():
        print("  ℹ️ Tabela pedidos não existe")
        return 0

    cursor.execute("SELECT * FROM pedidos LIMIT 100")
    pedidos = cursor.fetchall()

    count = 0

    for p in pedidos:
        p = dict(p)

        try:
            if not p.get("restaurante_id"):
                continue

            pedido = Pedido(
                restaurante_id=p["restaurante_id"],
                comanda=p["comanda"],
                tipo=p["tipo"],
                cliente_nome=p["cliente_nome"],
                cliente_telefone=p.get("cliente_telefone"),
                endereco_entrega=p.get("endereco_entrega"),
                numero_mesa=p.get("numero_mesa"),
                itens=p["itens"],
                observacoes=p.get("observacoes"),
                valor_total=p.get("valor_total", 0.0),
                tempo_estimado=p.get("tempo_estimado", 30),
                status=p.get("status", "pendente"),
                data_criacao=parse_datetime(p.get("data_criacao")) or datetime.utcnow(),
            )

            db_novo.add(pedido)
            count += 1

        except Exception as e:
            db_novo.rollback()
            print(f"  ❌ Erro pedido: {e}")

    db_novo.commit()
    print(f"✅ {count} pedidos migrados")
    return count


def executar_migracao():
    print("=" * 60)
    print("🚀 MIGRAÇÃO DE DADOS - SUPER FOOD SAAS")
    print("=" * 60)

    conn_antigo = conectar_banco_antigo()

    print("\n2️⃣ Inicializando banco novo...")
    init_db()

    print("\n3️⃣ Criando super admin...")
    criar_super_admin_padrao()

    if conn_antigo:
        db_novo = get_db_session()
        try:
            r = migrar_restaurantes(conn_antigo, db_novo)
            m = migrar_motoboys(conn_antigo, db_novo)
            p = migrar_pedidos(conn_antigo, db_novo)

            print("\n✅ MIGRAÇÃO FINALIZADA")
            print(f"• Restaurantes: {r}")
            print(f"• Motoboys: {m}")
            print(f"• Pedidos: {p}")

        finally:
            db_novo.close()
            conn_antigo.close()

    print("\n🎉 Sistema pronto para uso!")
    print("👤 superadmin / SuperFood2025!")


if __name__ == "__main__":
    executar_migracao()