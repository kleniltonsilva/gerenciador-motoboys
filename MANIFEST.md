# 🍕 SUPER FOOD - PROJECT MANIFEST
**Versão:** 2.0  
**Última Atualização:** 16/01/2026  
**Autor:** Klenilton Silva  
**Repositório:** https://github.com/kleniltonsilva/super-food

---

## 📋 VISÃO GERAL DO PROJETO

**Super Food** é um sistema SaaS multi-tenant para gestão de restaurantes com:
- 👑 Painel Super Admin (gerencia todos restaurantes)
- 🏪 Dashboard Restaurante (pedidos, motoboys, caixa)
- 🏍️ PWA Motoboy (app mobile-first)
- 🗺️ Integração Mapbox (rotas, GPS, geocoding)
- 💰 Gestão Financeira (planos, assinaturas, caixa)

---

## 🏗️ ARQUITETURA TÉCNICA

### **Stack Principal:**
- **Backend:** Python 3.9+
- **Banco de Dados:** SQLite (dev) → PostgreSQL (prod)
- **ORM:** SQLAlchemy 2.0+ 
- **Frontend:** Streamlit 1.40+
- **API Externa:** Mapbox (geocoding, rotas)
- **Migrations:** Alembic 1.13+

### **Dual Database System:**
O projeto usa **DOIS sistemas de banco em paralelo**:

1. **SQLite Direto** (`database.py`)
   - Funções SQL raw
   - Usado por: `restaurante_app.py`
   - Path: Raiz do projeto

2. **SQLAlchemy ORM** (`database/models.py`)
   - Models com relationships
   - Usado por: `super_admin.py`
   - Path: `database/`

---

## 📁 ESTRUTURA DE ARQUIVOS

```
super-food/
│
├── 📄 database.py                      # SQLite direto (DatabaseManager)
├── 🗄️ super_food.db                   # Banco SQLite (gerado)
├── 🔑 .env                             # Variáveis de ambiente
├── 📦 requirements.txt                 # Dependências Python
├── 📖 README.md                        # Documentação
├── 📜 LICENSE                          # Licença proprietária
├── 🖼️ logo.png                         # Logo do projeto
├── 🖼️ foto.png                         # Imagem ilustrativa
│
├── 📂 database/                        # SQLAlchemy ORM
│   ├── __init__.py
│   ├── base.py                        # Base declarativa
│   ├── models.py                      # Models (15 tabelas)
│   └── session.py                     # Session factory
│
├── 📂 migrations/                      # Alembic migrations
│   ├── env.py
│   ├── alembic.ini
│   └── versions/
│
├── 📂 streamlit_app/                   # Apps Streamlit
│   ├── __init__.py
│   ├── super_admin.py                 # 👑 Painel Super Admin
│   └── restaurante_app.py             # 🏪 Dashboard Restaurante
│
├── 📂 app_motoboy/                     # PWA Motoboy
│   ├── motoboy_app.py                 # 🏍️ Interface motoboy
│   ├── database.py                    # (cópia local)
│   └── requirements.txt
│
├── 📂 utils/                           # Utilitários
│   ├── __init__.py
│   ├── mapbox_api.py                  # Integração Mapbox
│   └── haversine.py                   # Cálculo distância
│
└── 📂 backend/ (FUTURO)                # FastAPI (opcional)
    └── app/
        ├── main.py
        ├── routers/
        └── dependencies/
```

---

## 🗄️ ESTRUTURA DO BANCO DE DADOS

### **15 Tabelas Principais:**

#### **1. SUPER ADMIN**
```sql
super_admin
├── id (PK)
├── usuario (UNIQUE)
├── senha_hash
└── data_criacao
```

#### **2. RESTAURANTES (Multi-Tenant)**
```sql
restaurantes
├── id (PK)
├── nome_fantasia
├── razao_social
├── cnpj
├── email (UNIQUE) ← Login
├── telefone
├── endereco_completo
├── latitude, longitude
├── plano (basico/essencial/avancado/premium)
├── valor_plano
├── limite_motoboys
├── status (ativo/suspenso/cancelado)
├── senha_hash
├── codigo_acesso (UNIQUE) ← Motoboys se cadastram com isso
├── data_criacao
└── data_vencimento
```

#### **3. CONFIG_RESTAURANTE**
```sql
config_restaurante
├── id (PK)
├── restaurante_id (FK, UNIQUE)
├── status_atual (aberto/fechado)
├── modo_despacho (auto_economico/manual/auto_ordem)
├── horario_abertura, horario_fechamento
├── dias_semana_abertos
├── valor_km, valor_lanche
├── taxa_entrega_base, distancia_base_km, taxa_km_extra
├── taxa_diaria
├── ifood_token, ifood_ativo
├── site_cliente_ativo
└── ultimo_login
```

#### **4. MOTOBOYS**
```sql
motoboys
├── id (PK)
├── restaurante_id (FK) ← Multi-tenant
├── nome
├── usuario (UNIQUE por restaurante)
├── senha_hash
├── telefone
├── codigo_acesso
├── status (disponivel/ocupado/offline)
├── aprovado (0/1)
├── data_cadastro, data_aprovacao
├── total_entregas
├── total_ganhos
└── avaliacao_media
```

#### **5. MOTOBOYS_SOLICITACOES**
```sql
motoboys_solicitacoes
├── id (PK)
├── restaurante_id (FK)
├── nome
├── usuario
├── telefone
├── codigo_acesso ← Informado pelo motoboy
├── data_solicitacao
├── status (pendente/aprovado/recusado)
└── motivo_recusa
```

#### **6. PEDIDOS**
```sql
pedidos
├── id (PK)
├── restaurante_id (FK)
├── comanda (UNIQUE por restaurante)
├── tipo (Entrega/Retirada na loja/Para mesa)
├── origem (manual/ifood/site)
├── cliente_nome, cliente_telefone
├── endereco_entrega
├── numero_mesa
├── latitude_cliente, longitude_cliente
├── itens (TEXT)
├── valor_total
├── observacoes
├── status (pendente/em_preparo/pronto/saiu_entrega/entregue/cancelado)
├── data_criacao
├── tempo_estimado
├── horario_previsto, horario_finalizado
├── prioridade
├── modo_despacho
└── despachado (0/1)
```

#### **7. ENTREGAS**
```sql
entregas
├── id (PK)
├── pedido_id (FK)
├── motoboy_id (FK)
├── restaurante_id (FK)
├── endereco_origem, endereco_destino
├── lat_origem, lon_origem, lat_destino, lon_destino
├── distancia_km
├── tempo_estimado_min
├── valor_entrega
├── ordem_rota
├── status (aguardando/em_rota/entregue/cancelado)
├── horario_atribuicao, horario_saida, horario_entrega
├── motivo_cancelamento
├── avaliacao_cliente
└── feedback_cliente
```

#### **8. CACHE_DISTANCIAS**
```sql
cache_distancias
├── id (PK)
├── restaurante_id (FK)
├── endereco_origem, endereco_origem_hash
├── endereco_destino, endereco_destino_hash
├── distancia_km
├── tempo_estimado_min
├── data_calculo
└── valido (0/1)
```

#### **9. CAIXA**
```sql
caixa
├── id (PK)
├── restaurante_id (FK)
├── data_abertura, data_fechamento
├── usuario_abertura, usuario_fechamento
├── valor_abertura, valor_fechamento
├── valor_retiradas
├── total_vendas
├── total_dinheiro, total_cartao, total_pix
├── status (aberto/fechado)
└── observacoes
```

#### **10. CAIXA_MOVIMENTACOES**
```sql
caixa_movimentacoes
├── id (PK)
├── caixa_id (FK)
├── restaurante_id (FK)
├── tipo (abertura/venda/retirada/fechamento)
├── valor
├── forma_pagamento
├── descricao
├── pedido_id (FK)
├── usuario
└── data_hora
```

#### **11. GPS_MOTOBOYS**
```sql
gps_motoboys
├── id (PK)
├── motoboy_id (FK)
├── restaurante_id (FK)
├── latitude, longitude
├── velocidade
├── precisao
└── timestamp
```

#### **12. RANKING_MOTOBOYS**
```sql
ranking_motoboys
├── id (PK)
├── restaurante_id (FK)
├── motoboy_id (FK)
├── periodo (diario/semanal/mensal)
├── data_inicio, data_fim
├── total_entregas, total_ganhos
├── total_distancia_km
├── tempo_medio_entrega_min
├── avaliacao_media
├── posicao_entregas, posicao_ganhos, posicao_velocidade
└── data_calculo
```

#### **13. CARDAPIO**
```sql
cardapio
├── id (PK)
├── restaurante_id (FK)
├── categoria
├── nome_item
├── descricao
├── preco
├── imagem_url
├── disponivel (0/1)
├── ordem
└── tempo_preparo
```

#### **14. NOTIFICACOES**
```sql
notificacoes
├── id (PK)
├── restaurante_id (FK)
├── motoboy_id (FK)
├── tipo
├── titulo
├── mensagem
├── lida (0/1)
├── data_criacao, data_leitura
└── dados_extra (JSON)
```

#### **15. ASSINATURAS**
```sql
assinaturas
├── id (PK)
├── restaurante_id (FK)
├── data_pagamento
├── valor_pago
├── forma_pagamento
├── status (ativo/vencido/cancelado)
├── data_vencimento
└── observacoes
```

---

## 🔧 FUNCIONALIDADES PRINCIPAIS

### **👑 SUPER ADMIN (`super_admin.py`)**
✅ Login seguro (SHA256)  
✅ Criar restaurantes  
✅ Gerenciar planos (Básico/Essencial/Avançado/Premium)  
✅ Renovar assinaturas  
✅ Suspender/Ativar/Cancelar restaurantes  
✅ Dashboard com métricas globais  
✅ Alertas de vencimento  

### **🏪 RESTAURANTE (`restaurante_app.py`)**
✅ Login com email + senha  
✅ Dashboard com métricas  
✅ Criar pedidos (Entrega/Retirada/Mesa)  
✅ Listar pedidos ativos  
✅ Histórico de pedidos  
✅ Aprovar/Recusar solicitações de motoboys  
✅ Gerenciar motoboys ativos  
✅ Configurar modo de despacho  
✅ Configurar pagamentos motoboys  
✅ Ranking de motoboys  
✅ Abrir/Fechar caixa  
✅ Registrar retiradas  
✅ Movimentações financeiras  
✅ Abrir/Fechar restaurante  
✅ Configurar horários  
✅ Notificações  

### **🏍️ MOTOBOY (`motoboy_app.py`)**
✅ Cadastro com código de acesso  
✅ Aguarda aprovação do restaurante  
✅ Login após aprovação  
✅ Receber entregas  
✅ Atualizar GPS  
✅ Histórico de ganhos  
✅ Ranking pessoal  

### **🗺️ MAPBOX (`utils/mapbox_api.py`)**
✅ Geocoding de endereços  
✅ Cálculo de rotas  
✅ Cache inteligente (economia 90% de requisições)  
✅ Fallback para Haversine  
✅ Cálculo de valor de entrega  

---

## 🔐 SEGURANÇA

- **Senhas:** Hash SHA256
- **Multi-tenant:** Isolamento completo por `restaurante_id`
- **Código de Acesso:** 6 dígitos únicos
- **Validações:** Email, CNPJ, telefone
- **Token Mapbox:** `.env` (nunca no código)

---

## 📊 PLANOS E LIMITES

| Plano | Valor/mês | Limite Motoboys |
|-------|-----------|-----------------|
| Básico | R$ 199,00 | 3 |
| Essencial | R$ 269,00 | 6 |
| Avançado | R$ 360,00 | 12 |
| Premium | R$ 599,00 | Ilimitado |

---

## 🚀 COMO EXECUTAR

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar .env
MAPBOX_TOKEN=seu_token_aqui

# 3. Executar apps
streamlit run streamlit_app/super_admin.py       # Porta 8501
streamlit run streamlit_app/restaurante_app.py   # Porta 8502
streamlit run app_motoboy/motoboy_app.py         # Porta 8503
```

### **Credenciais Padrão:**
- **Super Admin:** `superadmin` / `SuperFood2025!`
- **Restaurantes:** Email cadastrado / Primeiros 6 dígitos do telefone

---

## 🎯 MODO DE DESPACHO

### **1. 🧠 Automático Inteligente (Econômico)**
- Agrupa pedidos próximos
- Calcula rota otimizada
- Prioriza eficiência

### **2. ✋ Manual**
- Operador escolhe motoboy
- Total controle

### **3. ⏰ Automático por Ordem**
- Prioriza pedidos mais antigos
- Distribuição cronológica

---

## 🔄 FLUXOS PRINCIPAIS

### **Fluxo Pedido → Entrega:**
1. Restaurante cria pedido
2. Se tipo = "Entrega":
   - Geocodifica endereço (Mapbox)
   - Calcula distância
   - Se modo = "auto_economico": Atribui motoboy automaticamente
   - Se modo = "manual": Operador escolhe
3. Motoboy recebe notificação
4. Atualiza GPS em tempo real
5. Marca como entregue
6. Ranking atualizado

### **Fluxo Cadastro Motoboy:**
1. Motoboy informa código de acesso
2. Preenche dados (nome, usuário, telefone)
3. Solicitação fica pendente
4. Restaurante aprova/recusa
5. Se aprovado: Senha gerada automaticamente
6. Motoboy pode fazer login

---

## 📝 NOTAS IMPORTANTES

1. **Banco SQLite é temporário** - migrar para PostgreSQL em produção
2. **Dois sistemas de banco coexistem** - database.py (raw SQL) + models.py (ORM)
3. **Cache Mapbox** - essencial para economizar requisições
4. **Multi-tenant** - SEMPRE filtrar por `restaurante_id`
5. **Código de Acesso** - gerado automaticamente ao criar restaurante

---

## 🐛 ISSUES CONHECIDOS

- [ ] `restaurante_app.py` ainda usa SQLite direto
- [ ] `super_admin.py` usa SQLAlchemy
- [ ] Sincronização entre dois sistemas pode gerar inconsistências
- [ ] Migração para PostgreSQL pendente

---

## 🔮 ROADMAP (FUTURO)

### **Fase 1: Sistema de Rotas Inteligentes com IA**
- [ ] Adicionar campos de rotas em tabelas existentes
- [ ] Criar tabelas `rotas_motoboy` e `itens_rota`
- [ ] Implementar algoritmo TSP para otimização
- [ ] Validação de endereços via Mapbox
- [ ] Zona de cobertura por raio
- [ ] Tempo médio de preparo
- [ ] Despacho automático inteligente
- [ ] Alertas de motoboys insuficientes

### **Fase 2: Backend API (FastAPI)**
- [ ] Endpoints REST para todas operações
- [ ] Autenticação JWT
- [ ] WebSocket para GPS realtime
- [ ] Documentação OpenAPI

### **Fase 3: Site Cliente**
- [ ] Cardápio online
- [ ] Pedidos pelo site
- [ ] Rastreamento de entrega
- [ ] Pagamento online

### **Fase 4: Integração iFood**
- [ ] Sincronização automática de pedidos
- [ ] Status em tempo real
- [ ] Gestão unificada

---

## 📧 CONTATO

**Autor:** Klenilton Silva  
**GitHub:** https://github.com/kleniltonsilva  
**Repositório:** https://github.com/kleniltonsilva/super-food

---

## ⚖️ LICENÇA

**PROPRIETARY SOFTWARE — ALL RIGHTS RESERVED**

Este software é proprietário e confidencial.  
Nenhuma permissão é concedida sem autorização expressa.

---

**🍕 Super Food - Sistema SaaS Multi-Restaurante**  
*Última atualização: 16/01/2026*
