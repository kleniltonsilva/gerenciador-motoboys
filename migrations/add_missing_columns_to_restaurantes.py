# migrations/add_missing_columns_to_restaurantes.py
import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'super_food.db')

print("🔄 Iniciando migration para adicionar colunas faltantes na tabela restaurantes...")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Adiciona colunas uma por uma (SQLite permite apenas 1 coluna por ALTER TABLE)
alter_commands = [
    "ALTER TABLE restaurantes ADD COLUMN lat REAL DEFAULT -23.5505",
    "ALTER TABLE restaurantes ADD COLUMN lon REAL DEFAULT -46.6333",
    "ALTER TABLE restaurantes ADD COLUMN taxa_entrega REAL DEFAULT 0.0",
    "ALTER TABLE restaurantes ADD COLUMN tempo_medio_preparo INTEGER DEFAULT 30",
    "ALTER TABLE restaurantes ADD COLUMN codigo_acesso TEXT UNIQUE",
    "ALTER TABLE restaurantes ADD COLUMN ativo BOOLEAN DEFAULT 1"
]

for cmd in alter_commands:
    try:
        cursor.execute(cmd)
        print(f"✅ Coluna adicionada: {cmd.split(' ADD COLUMN ')[1].split(' ')[0]}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(f"⚠️ Coluna já existe: {cmd.split(' ADD COLUMN ')[1].split(' ')[0]}")
        else:
            print(f"❌ Erro ao adicionar coluna: {e}")

conn.commit()
conn.close()

print("✅ Migration concluída! Agora a tabela restaurantes tem todas as colunas necessárias.")
print("   Você pode continuar criando restaurantes normalmente.")