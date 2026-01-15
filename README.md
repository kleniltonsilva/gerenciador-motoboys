🍕 Super Food – Sistema Multi-Restaurante SaaS
�

�

⚠️ LICENSE NOTICE — IMPORTANT
🚫 THIS REPOSITORY IS NOT OPEN SOURCE
This source code is PROPRIETARY AND CONFIDENTIAL.
The code is made publicly visible solely for presentation and portfolio reference.
NO RIGHTS ARE GRANTED, including but not limited to:
❌ Use
❌ Copy
❌ Reproduce
❌ Modify
❌ Adapt
❌ Study for implementation
❌ Distribute
❌ Sublicense
❌ Sell
❌ Create derivative works
Any reproduction, storage, transmission, execution, or exploitation of this code — in whole or in part, by any means — is strictly prohibited without explicit prior written authorization from the copyright holder.
Violations may result in civil and criminal liability.
See the LICENSE file for full legal terms.
📌 About the Project
Sistema completo de gestão multi-restaurante SaaS, com despacho inteligente de entregas, rastreamento GPS em tempo real e gestão financeira integrada.
📋 Índice
Visão Geral
Funcionalidades
Arquitetura
Instalação
Configuração
Como Usar
Estrutura de Dados
API Mapbox
Licença
🎯 Visão Geral
O Super Food é uma plataforma SaaS proprietária para gestão de múltiplos restaurantes, oferecendo:
👑 Painel Super Admin — controle centralizado
🏪 Dashboard do Restaurante — pedidos, motoboys e caixa
🏍️ App PWA Motoboy — interface mobile-first
🗺️ Rastreamento GPS — localização em tempo real
💰 Gestão Financeira — caixa, planos e pagamentos
📊 Ranking e Relatórios — métricas operacionais
✨ Funcionalidades
👑 Super Admin
Criação e gerenciamento de restaurantes
Controle de planos e assinaturas
Métricas globais
Gestão de pagamentos
🏪 Dashboard Restaurante
Pedidos (Entrega, Retirada, Mesa)
Aprovação e gestão de motoboys
Despacho inteligente (automático/manual)
Controle de caixa
Configurações operacionais
🏍️ App Motoboy (PWA)
Cadastro com código de acesso
Aprovação pelo restaurante
Recebimento de entregas
GPS em tempo real
Histórico de ganhos
🏗️ Arquitetura
Copiar código

super-food/
├── database.py
├── super_food.db
├── super_admin.py
│
├── restaurante/
│   └── restaurante_app.py
│
├── app_motoboy/
│   └── motoboy_app.py
│
├── utils/
│   └── mapbox_api.py
│
├── .env
└── requirements.txt
🚀 Instalação
⚠️ Este projeto não é licenciado para uso externo.
As instruções abaixo existem apenas para fins demonstrativos do funcionamento técnico.
Pré-requisitos
Python 3.9+
pip
Conta Mapbox
Clone (visualização apenas)
Copiar código
Bash
git clone https://github.com/kleniltonsilva/super-food.git
cd super-food
⚙️ Configuração
Arquivo .env (exemplo ilustrativo):
Copiar código
Env
MAPBOX_TOKEN=example_token
DATABASE_PATH=super_food.db
DEBUG=True
📖 Como Usar
⚠️ Execução, teste ou deploy por terceiros NÃO É AUTORIZADO.
Os comandos abaixo são exibidos apenas para documentação técnica:
Copiar código
Bash
streamlit run super_admin.py
streamlit run restaurante/restaurante_app.py
streamlit run app_motoboy/motoboy_app.py
🗄️ Estrutura de Dados
15 tabelas integradas
Restaurantes
Motoboys
Pedidos
Entregas
Caixa
Cache de rotas
Rankings
🗺️ API Mapbox
Geocoding
Rotas
Cache inteligente
Economia de até 90% de requisições
📝 Licença
PROPRIETARY SOFTWARE — ALL RIGHTS RESERVED
Este software é proprietário e confidencial.
Nenhuma permissão é concedida para uso, cópia, reprodução, modificação, redistribuição ou criação de obras derivadas, sem autorização expressa e escrita do autor.
Consulte o arquivo LICENSE para os termos completos.
👤 Autor
Klenilton Silva
GitHub: https://github.com/kleniltonsilva
📊 Status do Projeto
✔ Ativo
✔ Em desenvolvimento contínuo
✔ Uso comercial exclusivo do autor
🚀 Super Food — Plataforma SaaS proprietária para gestão inteligente de restaurantes.
