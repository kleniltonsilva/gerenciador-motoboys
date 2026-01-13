"""
motoboy_app.py - App PWA para Motoboys
Sistema completo integrado com database.py
"""
import streamlit as st
import sys
import os
from datetime import datetime
import time
import hashlib

# Adicionar pasta raiz ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar database da raiz
try:
    from database import get_db
except ImportError:
    # Se não encontrar, tentar caminho alternativo
    import importlib.util
    spec = importlib.util.spec_from_file_location("database", os.path.join(os.path.dirname(__file__), '..', 'database.py'))
    database_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(database_module)
    get_db = database_module.get_db

# Configuração da página para PWA (mobile-friendly)
st.set_page_config(
    page_title="Motoboy App - Super Food",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS para mobile
st.markdown("""
<style>
    /* Mobile First Design */
    .stButton button {
        width: 100%;
        height: 60px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 10px;
        margin: 5px 0;
    }
    
    .stButton button[kind="primary"] {
        background-color: #00AA00;
        color: white;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    
    .status-disponivel {
        background-color: #00AA00;
        color: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-size: 20px;
        font-weight: bold;
    }
    
    .status-ocupado {
        background-color: #FFA500;
        color: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-size: 20px;
        font-weight: bold;
    }
    
    .pedido-card {
        background: white;
        border: 2px solid #ddd;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .map-container {
        border-radius: 15px;
        overflow: hidden;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== AUTENTICAÇÃO ====================

def verificar_login():
    """Verifica se motoboy está logado"""
    if 'motoboy_logado' not in st.session_state:
        st.session_state.motoboy_logado = False
        st.session_state.motoboy_id = None
        st.session_state.motoboy_dados = None
        st.session_state.restaurante_id = None

def fazer_login_motoboy(usuario: str, senha: str) -> bool:
    """Faz login do motoboy"""
    db = get_db()
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT m.*, r.nome_fantasia as restaurante_nome, r.endereco_completo as restaurante_endereco
        FROM motoboys m
        JOIN restaurantes r ON m.restaurante_id = r.id
        WHERE m.usuario = ? AND m.senha_hash = ? AND m.aprovado = 1
    """, (usuario, senha_hash))
    
    motoboy = cursor.fetchone()
    
    if motoboy:
        st.session_state.motoboy_logado = True
        st.session_state.motoboy_id = motoboy['id']
        st.session_state.motoboy_dados = dict(motoboy)
        st.session_state.restaurante_id = motoboy['restaurante_id']
        return True
    
    return False

def fazer_logout():
    """Faz logout do motoboy"""
    st.session_state.motoboy_logado = False
    st.session_state.motoboy_id = None
    st.session_state.motoboy_dados = None
    st.session_state.restaurante_id = None

# ==================== TELA DE CADASTRO ====================

def tela_cadastro():
    """Interface de cadastro do motoboy"""
    st.title("🏍️ Cadastro de Motoboy")
    st.markdown("### Solicite seu cadastro")
    
    with st.form("form_cadastro_motoboy"):
        codigo_acesso = st.text_input(
            "Código de Acesso do Restaurante *",
            placeholder="Digite o código de 6 dígitos",
            max_chars=6,
            help="Solicite o código ao restaurante"
        )
        
        st.markdown("---")
        
        nome = st.text_input("Seu Nome Completo *", placeholder="Ex: João Silva")
        usuario = st.text_input("Escolha um Usuário *", placeholder="Ex: joao123")
        telefone = st.text_input("Telefone/WhatsApp *", placeholder="(11) 99999-9999")
        senha = st.text_input("Escolha uma Senha *", type="password", placeholder="Mínimo 6 caracteres")
        confirmar_senha = st.text_input("Confirme a Senha *", type="password")
        
        submit = st.form_submit_button("📤 Solicitar Cadastro", use_container_width=True, type="primary")
        
        if submit:
            # Validações
            erros = []
            
            if not codigo_acesso or len(codigo_acesso) != 6:
                erros.append("Código de acesso deve ter 6 dígitos")
            
            if not nome or len(nome.strip()) < 3:
                erros.append("Nome deve ter pelo menos 3 caracteres")
            
            if not usuario or len(usuario.strip()) < 3:
                erros.append("Usuário deve ter pelo menos 3 caracteres")
            
            if not telefone or len(telefone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')) < 10:
                erros.append("Telefone inválido")
            
            if not senha or len(senha) < 6:
                erros.append("Senha deve ter pelo menos 6 caracteres")
            
            if senha != confirmar_senha:
                erros.append("As senhas não coincidem")
            
            if erros:
                for erro in erros:
                    st.error(f"❌ {erro}")
            else:
                # Buscar restaurante pelo código
                db = get_db()
                conn = db.get_connection()
                cursor = conn.cursor()
                
                cursor.execute("SELECT id FROM restaurantes WHERE codigo_acesso = ?", (codigo_acesso,))
                restaurante = cursor.fetchone()
                
                if not restaurante:
                    st.error("❌ Código de acesso inválido!")
                else:
                    dados = {
                        'restaurante_id': restaurante['id'],
                        'nome': nome.strip(),
                        'usuario': usuario.strip().lower(),
                        'telefone': ''.join(filter(str.isdigit, telefone)),
                        'codigo_acesso': codigo_acesso
                    }
                    
                    # Senha temporária (será criada na aprovação)
                    dados['senha_temp'] = senha
                    
                    sucesso, msg = db.criar_solicitacao_motoboy(dados)
                    
                    if sucesso:
                        st.success(f"✅ {msg}")
                        st.balloons()
                        st.info("💡 Aguarde a aprovação do restaurante. Você receberá uma notificação!")
                        time.sleep(3)
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
    
    st.markdown("---")
    
    if st.button("🔙 Voltar para Login", use_container_width=True):
        st.session_state.tela_atual = "login"
        st.rerun()

# ==================== TELA DE LOGIN ====================

def tela_login():
    """Interface de login do motoboy"""
    st.title("🏍️ Motoboy App")
    st.markdown("### 🔐 Faça seu Login")
    
    with st.form("form_login_motoboy"):
        usuario = st.text_input("Usuário", placeholder="Seu usuário")
        senha = st.text_input("Senha", type="password", placeholder="Sua senha")
        
        col1, col2 = st.columns(2)
        
        with col1:
            submit = st.form_submit_button("🚀 Entrar", use_container_width=True, type="primary")
        
        with col2:
            cadastro = st.form_submit_button("📝 Cadastrar", use_container_width=True)
        
        if submit:
            if not usuario or not senha:
                st.error("❌ Preencha todos os campos!")
            elif fazer_login_motoboy(usuario, senha):
                st.success("✅ Login realizado!")
                st.rerun()
            else:
                st.error("❌ Usuário ou senha incorretos, ou cadastro não aprovado!")
        
        if cadastro:
            st.session_state.tela_atual = "cadastro"
            st.rerun()
    
    st.markdown("---")
    st.info("💡 **Não tem cadastro?** Clique em 'Cadastrar' e solicite seu acesso ao restaurante!")

# ==================== MAPA EM TEMPO REAL ====================

def tela_mapa():
    """Mapa com localização em tempo real"""
    st.title("🗺️ Sua Localização")
    
    motoboy = st.session_state.motoboy_dados
    
    st.markdown(f"### 👤 Olá, {motoboy['nome']}!")
    st.markdown(f"**Restaurante:** {motoboy['restaurante_nome']}")
    
    # Buscar última posição GPS
    db = get_db()
    posicao = db.buscar_ultima_posicao_motoboy(st.session_state.motoboy_id)
    
    if posicao:
        st.success(f"📍 Última atualização: {posicao['timestamp']}")
        st.markdown(f"**Latitude:** {posicao['latitude']}")
        st.markdown(f"**Longitude:** {posicao['longitude']}")
        st.markdown(f"**Velocidade:** {posicao['velocidade']:.1f} km/h")
    else:
        st.info("📍 Aguardando primeira atualização de localização...")
    
    st.markdown("---")
    
    # Simular atualização de GPS (em produção seria automático via GPS do celular)
    st.markdown("### 📡 Atualizar Localização")
    
    with st.form("form_atualizar_gps"):
        col1, col2 = st.columns(2)
        
        with col1:
            lat = st.number_input("Latitude", value=-23.550520, format="%.6f")
        
        with col2:
            lon = st.number_input("Longitude", value=-46.633308, format="%.6f")
        
        velocidade = st.number_input("Velocidade (km/h)", min_value=0.0, max_value=120.0, value=0.0)
        
        if st.form_submit_button("📍 Atualizar Posição", use_container_width=True, type="primary"):
            if db.atualizar_gps_motoboy(
                st.session_state.motoboy_id,
                st.session_state.restaurante_id,
                lat,
                lon,
                velocidade
            ):
                st.success("✅ Localização atualizada!")
                st.rerun()
            else:
                st.error("❌ Erro ao atualizar localização!")

# ==================== ENTREGAS ====================

def tela_entregas():
    """Tela de entregas disponíveis e em andamento"""
    st.title("📦 Suas Entregas")
    
    motoboy = st.session_state.motoboy_dados
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Buscar entregas do motoboy
    cursor.execute("""
        SELECT e.*, p.comanda, p.cliente_nome, p.cliente_telefone, 
               p.endereco_entrega, p.observacoes
        FROM entregas e
        JOIN pedidos p ON e.pedido_id = p.id
        WHERE e.motoboy_id = ? AND e.status IN ('aguardando', 'em_rota')
        ORDER BY e.ordem_rota
    """, (st.session_state.motoboy_id,))
    
    entregas = [dict(row) for row in cursor.fetchall()]
    
    # Status do motoboy
    if entregas:
        if any(e['status'] == 'em_rota' for e in entregas):
            st.markdown('<div class="status-ocupado">🏍️ EM ROTA</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-disponivel">✅ ENTREGAS ATRIBUÍDAS</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-disponivel">✅ DISPONÍVEL</div>', unsafe_allow_html=True)
        st.info("⏳ Aguardando pedidos...")
        return
    
    st.markdown(f"### 📦 {len(entregas)} entrega(s) na fila")
    
    st.markdown("---")
    
    # Mostrar apenas a primeira entrega (as outras ficam ocultas)
    primeira_entrega = entregas[0]
    outras_entregas = entregas[1:] if len(entregas) > 1 else []
    
    st.markdown("### 🎯 Próxima Entrega:")
    
    st.markdown(f"""
    <div class="pedido-card">
        <h3>📦 Comanda #{primeira_entrega['comanda']}</h3>
        <p><strong>👤 Cliente:</strong> {primeira_entrega['cliente_nome']}</p>
        <p><strong>📞 Telefone:</strong> {primeira_entrega['cliente_telefone']}</p>
        <p><strong>📍 Endereço:</strong> {primeira_entrega['endereco_destino']}</p>
        <p><strong>📏 Distância:</strong> {primeira_entrega['distancia_km']:.2f} km</p>
        <p><strong>⏱️ Tempo Estimado:</strong> {primeira_entrega['tempo_estimado_min']} min</p>
        <p><strong>💰 Valor da Entrega:</strong> R$ {primeira_entrega['valor_entrega']:.2f}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if primeira_entrega['observacoes']:
        st.warning(f"📝 **Observações:** {primeira_entrega['observacoes']}")
    
    st.markdown("---")
    
    # Ações baseadas no status
    if primeira_entrega['status'] == 'aguardando':
        st.markdown("### ⚡ Ações:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📞 Ligar para Cliente", use_container_width=True):
                st.info(f"📞 Ligando para {primeira_entrega['cliente_telefone']}...")
                # Em produção, abriria o app de telefone
        
        with col2:
            if st.button("🚀 Iniciar Rota", use_container_width=True, type="primary"):
                # Atualizar status para em_rota
                cursor.execute(
                    "UPDATE entregas SET status = 'em_rota', horario_saida = ? WHERE id = ?",
                    (datetime.now(), primeira_entrega['id'])
                )
                conn.commit()
                
                st.success("✅ Rota iniciada!")
                st.info("🗺️ Abrindo navegação...")
                # Em produção, abriria Waze ou Google Maps
                st.markdown(f"""
                **Navegue até:**
                {primeira_entrega['endereco_destino']}
                
                [Abrir no Google Maps](https://www.google.com/maps/search/?api=1&query={primeira_entrega['endereco_destino']})
                """)
                
                time.sleep(2)
                st.rerun()
    
    elif primeira_entrega['status'] == 'em_rota':
        st.success("🏍️ Você está em rota!")
        
        st.markdown("### ⚡ Ações na Entrega:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📞 Ligar para Cliente", use_container_width=True):
                st.info(f"📞 Ligando para {primeira_entrega['cliente_telefone']}...")
        
        with col2:
            if st.button("✅ Entregar Pedido", use_container_width=True, type="primary"):
                # Atualizar status para entregue
                cursor.execute(
                    "UPDATE entregas SET status = 'entregue', horario_entrega = ? WHERE id = ?",
                    (datetime.now(), primeira_entrega['id'])
                )
                
                # Atualizar pedido
                cursor.execute(
                    "UPDATE pedidos SET status = 'entregue', horario_finalizado = ? WHERE id = ?",
                    (datetime.now(), primeira_entrega['pedido_id'])
                )
                
                conn.commit()
                
                # Atualizar estatísticas do motoboy
                db.atualizar_ranking_motoboy(st.session_state.motoboy_id, st.session_state.restaurante_id)
                
                st.success("✅ Pedido entregue com sucesso!")
                st.balloons()
                
                time.sleep(2)
                st.rerun()
        
        st.markdown("---")
        
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button("❌ Pedido Rejeitado", use_container_width=True):
                st.session_state.modal_rejeitar = True
                st.rerun()
        
        with col4:
            if st.button("🚪 Cliente Ausente", use_container_width=True):
                st.session_state.modal_ausente = True
                st.rerun()
    
    # Modais
    if st.session_state.get('modal_rejeitar'):
        modal_rejeitar_pedido(primeira_entrega)
    
    if st.session_state.get('modal_ausente'):
        modal_cliente_ausente(primeira_entrega)
    
    # Mostrar outras entregas na fila
    if outras_entregas:
        st.markdown("---")
        st.markdown(f"### 📋 Próximas entregas ({len(outras_entregas)}):")
        
        for i, entrega in enumerate(outras_entregas, start=2):
            with st.expander(f"#{i} - Comanda {entrega['comanda']} - {entrega['distancia_km']:.1f} km"):
                st.markdown(f"**Cliente:** {entrega['cliente_nome']}")
                st.markdown(f"**Endereço:** {entrega['endereco_destino']}")
                st.markdown(f"**Valor:** R$ {entrega['valor_entrega']:.2f}")

def modal_rejeitar_pedido(entrega):
    """Modal para rejeitar pedido"""
    with st.form("form_rejeitar"):
        st.warning("⚠️ Rejeitar Pedido")
        st.markdown("Por que você está rejeitando este pedido?")
        
        motivo = st.text_area("Motivo", placeholder="Explique o motivo...")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("❌ Confirmar Rejeição", use_container_width=True):
                db = get_db()
                conn = db.get_connection()
                cursor = conn.cursor()
                
                cursor.execute(
                    "UPDATE entregas SET status = 'cancelado', motivo_cancelamento = ? WHERE id = ?",
                    (motivo, entrega['id'])
                )
                conn.commit()
                
                st.error("❌ Pedido rejeitado!")
                st.session_state.modal_rejeitar = False
                time.sleep(2)
                st.rerun()
        
        with col2:
            if st.form_submit_button("🔙 Cancelar", use_container_width=True):
                st.session_state.modal_rejeitar = False
                st.rerun()

def modal_cliente_ausente(entrega):
    """Modal para cliente ausente"""
    with st.form("form_ausente"):
        st.warning("🚪 Cliente Ausente")
        st.markdown("O que você fez?")
        
        acao = st.radio(
            "Ação tomada:",
            ["Tentei ligar e não atendeu", "Bati na porta e não respondeu", "Aguardei no local"]
        )
        
        observacoes = st.text_area("Observações adicionais")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("✅ Registrar", use_container_width=True):
                db = get_db()
                conn = db.get_connection()
                cursor = conn.cursor()
                
                cursor.execute(
                    "UPDATE entregas SET status = 'cancelado', motivo_cancelamento = ? WHERE id = ?",
                    (f"Cliente ausente: {acao}. {observacoes}", entrega['id'])
                )
                conn.commit()
                
                st.warning("⚠️ Registrado como cliente ausente!")
                st.session_state.modal_ausente = False
                time.sleep(2)
                st.rerun()
        
        with col2:
            if st.form_submit_button("🔙 Cancelar", use_container_width=True):
                st.session_state.modal_ausente = False
                st.rerun()

# ==================== GANHOS ====================

def tela_ganhos():
    """Tela de ganhos e histórico"""
    st.title("💰 Seus Ganhos")
    
    motoboy = st.session_state.motoboy_dados
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Buscar estatísticas
    cursor.execute("""
        SELECT 
            COUNT(*) as total_entregas,
            SUM(valor_entrega) as total_ganho,
            SUM(distancia_km) as total_km
        FROM entregas
        WHERE motoboy_id = ? AND status = 'entregue'
    """, (st.session_state.motoboy_id,))
    
    stats = dict(cursor.fetchone())
    
    # Cards de métricas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{stats['total_entregas'] or 0}</h2>
            <p>Entregas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h2>R$ {stats['total_ganho'] or 0:.2f}</h2>
            <p>Total Ganho</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{stats['total_km'] or 0:.1f} km</h2>
            <p>Distância</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Histórico de entregas
    st.subheader("📜 Histórico de Entregas")
    
    cursor.execute("""
        SELECT e.*, p.comanda, p.cliente_nome
        FROM entregas e
        JOIN pedidos p ON e.pedido_id = p.id
        WHERE e.motoboy_id = ? AND e.status = 'entregue'
        ORDER BY e.horario_entrega DESC
        LIMIT 20
    """, (st.session_state.motoboy_id,))
    
    historico = [dict(row) for row in cursor.fetchall()]
    
    if not historico:
        st.info("Nenhuma entrega realizada ainda.")
    else:
        for entrega in historico:
            with st.expander(f"📦 Comanda {entrega['comanda']} - R$ {entrega['valor_entrega']:.2f}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Cliente:** {entrega['cliente_nome']}")
                    st.markdown(f"**Distância:** {entrega['distancia_km']:.2f} km")
                
                with col2:
                    st.markdown(f"**Valor:** R$ {entrega['valor_entrega']:.2f}")
                    st.markdown(f"**Data:** {entrega['horario_entrega'][:16]}")

# ==================== PERFIL ====================

def tela_perfil():
    """Tela de perfil do motoboy"""
    st.title("👤 Meu Perfil")
    
    motoboy = st.session_state.motoboy_dados
    
    st.markdown(f"### {motoboy['nome']}")
    st.markdown(f"**Usuário:** {motoboy['usuario']}")
    st.markdown(f"**Telefone:** {motoboy['telefone']}")
    st.markdown(f"**Restaurante:** {motoboy['restaurante_nome']}")
    
    st.markdown("---")
    
    st.markdown("### 📊 Estatísticas")
    st.metric("Total de Entregas", motoboy['total_entregas'])
    st.metric("Total Ganho", f"R$ {motoboy['total_ganhos']:.2f}")
    
    st.markdown("---")
    
    if st.button("🚪 Sair", use_container_width=True, type="primary"):
        fazer_logout()
        st.rerun()

# ==================== MENU INFERIOR (BOTTOM NAV) ====================

def menu_inferior():
    """Menu de navegação inferior (mobile style)"""
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🗺️\nMapa", use_container_width=True):
            st.session_state.tela_atual = "mapa"
            st.rerun()
    
    with col2:
        if st.button("📦\nEntregas", use_container_width=True):
            st.session_state.tela_atual = "entregas"
            st.rerun()
    
    with col3:
        if st.button("💰\nGanhos", use_container_width=True):
            st.session_state.tela_atual = "ganhos"
            st.rerun()
    
    with col4:
        if st.button("👤\nPerfil", use_container_width=True):
            st.session_state.tela_atual = "perfil"
            st.rerun()

# ==================== MAIN ====================

def main():
    """Função principal"""
    verificar_login()
    
    # Inicializar tela atual
    if 'tela_atual' not in st.session_state:
        st.session_state.tela_atual = "entregas"
    
    if not st.session_state.motoboy_logado:
        # Tela de login ou cadastro
        if st.session_state.get('tela_atual') == "cadastro":
            tela_cadastro()
        else:
            tela_login()
    else:
        # App do motoboy logado
        tela = st.session_state.tela_atual
        
        if tela == "mapa":
            tela_mapa()
        elif tela == "entregas":
            tela_entregas()
        elif tela == "ganhos":
            tela_ganhos()
        elif tela == "perfil":
            tela_perfil()
        else:
            tela_entregas()
        
        # Menu inferior
        menu_inferior()

if __name__ == "__main__":
    main()