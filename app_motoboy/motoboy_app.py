"""
motoboy_app.py - App PWA para Motoboys
Adaptado para o novo banco de dados SQLAlchemy (usado pelo script de migração)

CORREÇÃO ADICIONAL APLICADA:
- Todas as consultas agora usam .mappings() para garantir acesso dict-like seguro (evita TypeError de tuple).
- Exemplo: result.mappings().fetchone() → row['id']
- Isso é padrão no SQLAlchemy core para queries raw.
- Nenhuma outra mudança – UI, fluxo e validações permanecem 100% iguais ao código original que você enviou.
"""

import streamlit as st
import sys
import os
from datetime import datetime
import time
import hashlib
from sqlalchemy import text

# Adicionar pasta raiz ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar session do novo banco SQLAlchemy
from database.session import get_db_session

# Configuração da página para PWA (mobile-friendly)
st.set_page_config(
    page_title="Motoboy App - Super Food",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS para mobile (inalterado)
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
    """Faz login do motoboy (corrigido para colunas reais: senha e status = 'ativo')"""
    session = get_db_session()
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    
    result = session.execute(text("""
        SELECT m.*, r.nome_fantasia as restaurante_nome, r.endereco_completo as restaurante_endereco
        FROM motoboys m
        JOIN restaurantes r ON m.restaurante_id = r.id
        WHERE m.usuario = :usuario AND m.senha = :senha_hash AND m.status = 'ativo'
    """), {"usuario": usuario, "senha_hash": senha_hash})
    
    motoboy_row = result.mappings().fetchone()
    
    if motoboy_row:
        motoboy = dict(motoboy_row)
        st.session_state.motoboy_logado = True
        st.session_state.motoboy_id = motoboy['id']
        st.session_state.motoboy_dados = motoboy
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
    """Interface de cadastro do motoboy (sem senha – definida na aprovação)"""
    st.title("🏍️ Cadastro de Motoboy")
    st.markdown("### Solicite seu cadastro")
    
    with st.form("form_cadastro_motoboy"):
        codigo_acesso = st.text_input(
            "Código de Acesso do Restaurante *",
            placeholder="Digite o código de 8 dígitos",
            max_chars=8,
            help="Solicite o código ao restaurante"
        )
        
        st.markdown("---")
        
        nome = st.text_input("Seu Nome Completo *", placeholder="Ex: João Silva")
        usuario = st.text_input("Escolha um Usuário *", placeholder="Ex: joao123")
        telefone = st.text_input("Telefone/WhatsApp *", placeholder="(11) 99999-9999")
        
        st.info("🔐 Após aprovação pelo restaurante, sua senha inicial será **123456**.")
        
        submit = st.form_submit_button("📤 Solicitar Cadastro", use_container_width=True, type="primary")
        
        if submit:
            # Validações
            erros = []
            
            if not codigo_acesso or len(codigo_acesso.strip()) != 8:
                erros.append("Código de acesso deve ter 8 dígitos")
            
            if not nome or len(nome.strip()) < 3:
                erros.append("Nome deve ter pelo menos 3 caracteres")
            
            if not usuario or len(usuario.strip()) < 3:
                erros.append("Usuário deve ter pelo menos 3 caracteres")
            
            if not telefone or len(''.join(filter(str.isdigit, telefone))) < 10:
                erros.append("Telefone inválido")
            
            if erros:
                for erro in erros:
                    st.error(f"❌ {erro}")
            else:
                codigo_limpo = codigo_acesso.strip().upper()
                telefone_limpo = ''.join(filter(str.isdigit, telefone))
                
                session = get_db_session()
                
                # Validação do código
                result = session.execute(text("""
                    SELECT id FROM restaurantes 
                    WHERE codigo_acesso = :codigo AND ativo = True
                """), {"codigo": codigo_limpo})
                
                restaurante_row = result.mappings().fetchone()
                
                if not restaurante_row:
                    st.error("❌ Código de acesso inválido!")
                else:
                    restaurante_id = restaurante_row['id']
                    
                    # Inserção na tabela de solicitações
                    try:
                        session.execute(text("""
                            INSERT INTO motoboys_solicitacoes (
                                restaurante_id, nome, usuario, telefone, codigo_acesso, data_solicitacao, status
                            ) VALUES (:restaurante_id, :nome, :usuario, :telefone, :codigo_acesso, :data, 'pendente')
                        """), {
                            "restaurante_id": restaurante_id,
                            "nome": nome.strip(),
                            "usuario": usuario.strip().lower(),
                            "telefone": telefone_limpo,
                            "codigo_acesso": codigo_limpo,
                            "data": datetime.now()
                        })
                        session.commit()
                        
                        st.success("✅ Solicitação enviada! Aguarde aprovação do restaurante.")
                        st.balloons()
                        st.info("💡 Quando aprovado, use a senha padrão **123456** para login.")
                        time.sleep(3)
                        st.rerun()
                    except Exception as e:
                        session.rollback()
                        st.error(f"❌ Erro ao enviar solicitação: {str(e)}")
    
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
        senha = st.text_input("Senha", type="password", placeholder="Senha (padrão: 123456)")
        
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
    
    session = get_db_session()
    
    result = session.execute(text("""
        SELECT * FROM gps_motoboys 
        WHERE motoboy_id = :mid 
        ORDER BY timestamp DESC LIMIT 1
    """), {"mid": st.session_state.motoboy_id})
    
    posicao_row = result.mappings().fetchone()
    
    if posicao_row:
        posicao = dict(posicao_row)
        st.success(f"📍 Última atualização: {posicao['timestamp']}")
        st.markdown(f"**Latitude:** {posicao['latitude']}")
        st.markdown(f"**Longitude:** {posicao['longitude']}")
        st.markdown(f"**Velocidade:** {posicao['velocidade']:.1f} km/h")
    else:
        st.info("📍 Aguardando primeira atualização de localização...")
    
    st.markdown("---")
    
    st.markdown("### 📡 Atualizar Localização")
    
    with st.form("form_atualizar_gps"):
        col1, col2 = st.columns(2)
        
        with col1:
            lat = st.number_input("Latitude", value=-23.550520, format="%.6f")
        
        with col2:
            lon = st.number_input("Longitude", value=-46.633308, format="%.6f")
        
        velocidade = st.number_input("Velocidade (km/h)", min_value=0.0, max_value=120.0, value=0.0)
        
        if st.form_submit_button("📍 Atualizar Posição", use_container_width=True, type="primary"):
            try:
                session.execute(text("""
                    INSERT INTO gps_motoboys (
                        motoboy_id, restaurante_id, latitude, longitude, velocidade, timestamp
                    ) VALUES (:mid, :rid, :lat, :lon, :vel, :ts)
                """), {
                    "mid": st.session_state.motoboy_id,
                    "rid": st.session_state.restaurante_id,
                    "lat": lat,
                    "lon": lon,
                    "vel": velocidade,
                    "ts": datetime.now()
                })
                session.commit()
                st.success("✅ Localização atualizada!")
                st.rerun()
            except Exception as e:
                session.rollback()
                st.error(f"❌ Erro ao atualizar localização: {str(e)}")

# ==================== ENTREGAS ====================

def tela_entregas():
    """Tela de entregas (corrigida ORDER BY para coluna real)"""
    st.title("📦 Suas Entregas")
    
    session = get_db_session()
    
    result = session.execute(text("""
        SELECT e.*, p.comanda, p.cliente_nome, p.cliente_telefone, 
               p.endereco_entrega, p.observacoes
        FROM entregas e
        JOIN pedidos p ON e.pedido_id = p.id
        WHERE e.motoboy_id = :mid AND e.status IN ('aguardando', 'em_rota')
        ORDER BY e.atribuido_em ASC
    """), {"mid": st.session_state.motoboy_id})
    
    entregas = [dict(row) for row in result.mappings().fetchall()]
    
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
    
    primeira_entrega = entregas[0]
    outras_entregas = entregas[1:] if len(entregas) > 1 else []
    
    st.markdown("### 🎯 Próxima Entrega:")
    
    st.markdown(f"""
    <div class="pedido-card">
        <h3>📦 Comanda #{primeira_entrega['comanda']}</h3>
        <p><strong>👤 Cliente:</strong> {primeira_entrega['cliente_nome']}</p>
        <p><strong>📞 Telefone:</strong> {primeira_entrega['cliente_telefone']}</p>
        <p><strong>📍 Endereço:</strong> {primeira_entrega['endereco_entrega']}</p>
        <p><strong>📏 Distância:</strong> {primeira_entrega['distancia_km']:.2f} km</p>
        <p><strong>⏱️ Tempo Estimado:</strong> {primeira_entrega['tempo_entrega']} min</p>
        <p><strong>💰 Valor da Entrega:</strong> R$ {primeira_entrega['valor_entrega']:.2f}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if primeira_entrega.get('observacoes'):
        st.warning(f"📝 **Observações:** {primeira_entrega['observacoes']}")
    
    st.markdown("---")
    
    if primeira_entrega['status'] == 'aguardando':
        st.markdown("### ⚡ Ações:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📞 Ligar para Cliente", use_container_width=True):
                st.info(f"📞 Ligando para {primeira_entrega['cliente_telefone']}...")
        
        with col2:
            if st.button("🚀 Iniciar Rota", use_container_width=True, type="primary"):
                try:
                    session.execute(text("""
                        UPDATE entregas SET status = 'em_rota', horario_saida = :now WHERE id = :eid
                    """), {"now": datetime.now(), "eid": primeira_entrega['id']})
                    session.commit()
                    st.success("✅ Rota iniciada!")
                    st.info("🗺️ Abrindo navegação...")
                    st.markdown(f"""
                    **Navegue até:**
                    {primeira_entrega['endereco_entrega']}
                    
                    [Abrir no Google Maps](https://www.google.com/maps/search/?api=1&query={primeira_entrega['endereco_entrega']})
                    """)
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    session.rollback()
                    st.error(f"Erro: {str(e)}")
    
    elif primeira_entrega['status'] == 'em_rota':
        st.success("🏍️ Você está em rota!")
        
        st.markdown("### ⚡ Ações na Entrega:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📞 Ligar para Cliente", use_container_width=True):
                st.info(f"📞 Ligando para {primeira_entrega['cliente_telefone']}...")
        
        with col2:
            if st.button("✅ Entregar Pedido", use_container_width=True, type="primary"):
                try:
                    session.execute(text("""
                        UPDATE entregas SET status = 'entregue', horario_entrega = :now WHERE id = :eid
                    """), {"now": datetime.now(), "eid": primeira_entrega['id']})
                    
                    session.execute(text("""
                        UPDATE pedidos SET status = 'entregue', horario_finalizado = :now WHERE id = :pid
                    """), {"now": datetime.now(), "pid": primeira_entrega['pedido_id']})
                    
                    session.execute(text("""
                        UPDATE motoboys SET
                            total_entregas = (
                                SELECT COUNT(*) FROM entregas 
                                WHERE motoboy_id = :mid AND status = 'entregue'
                            ),
                            total_ganhos = (
                                SELECT COALESCE(SUM(valor_entrega), 0) FROM entregas 
                                WHERE motoboy_id = :mid AND status = 'entregue'
                            )
                        WHERE id = :mid
                    """), {"mid": st.session_state.motoboy_id})
                    session.commit()
                    
                    st.success("✅ Pedido entregue com sucesso!")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    session.rollback()
                    st.error(f"Erro: {str(e)}")
        
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
    
    if st.session_state.get('modal_rejeitar'):
        modal_rejeitar_pedido(primeira_entrega, session)
    
    if st.session_state.get('modal_ausente'):
        modal_cliente_ausente(primeira_entrega, session)
    
    if outras_entregas:
        st.markdown("---")
        st.markdown(f"### 📋 Próximas entregas ({len(outras_entregas)}):")
        
        for i, entrega in enumerate(outras_entregas, start=2):
            with st.expander(f"#{i} - Comanda {entrega['comanda']} - {entrega['distancia_km']:.1f} km"):
                st.markdown(f"**Cliente:** {entrega['cliente_nome']}")
                st.markdown(f"**Endereço:** {entrega['endereco_entrega']}")
                st.markdown(f"**Valor:** R$ {entrega['valor_entrega']:.2f}")

def modal_rejeitar_pedido(entrega, session):
    with st.form("form_rejeitar"):
        st.warning("⚠️ Rejeitar Pedido")
        st.markdown("Por que você está rejeitando este pedido?")
        
        motivo = st.text_area("Motivo", placeholder="Explique o motivo...")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("❌ Confirmar Rejeição", use_container_width=True):
                try:
                    session.execute(text("""
                        UPDATE entregas SET status = 'cancelado', motivo_cancelamento = :motivo WHERE id = :eid
                    """), {"motivo": motivo, "eid": entrega['id']})
                    session.commit()
                    st.error("❌ Pedido rejeitado!")
                    st.session_state.modal_rejeitar = False
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    session.rollback()
                    st.error(f"Erro: {str(e)}")
        
        with col2:
            if st.form_submit_button("🔙 Cancelar", use_container_width=True):
                st.session_state.modal_rejeitar = False
                st.rerun()

def modal_cliente_ausente(entrega, session):
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
                try:
                    motivo = f"Cliente ausente: {acao}. {observacoes}"
                    session.execute(text("""
                        UPDATE entregas SET status = 'cancelado', motivo_cancelamento = :motivo WHERE id = :eid
                    """), {"motivo": motivo, "eid": entrega['id']})
                    session.commit()
                    st.warning("⚠️ Registrado como cliente ausente!")
                    st.session_state.modal_ausente = False
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    session.rollback()
                    st.error(f"Erro: {str(e)}")
        
        with col2:
            if st.form_submit_button("🔙 Cancelar", use_container_width=True):
                st.session_state.modal_ausente = False
                st.rerun()

# ==================== GANHOS ====================

def tela_ganhos():
    session = get_db_session()
    
    result = session.execute(text("""
        SELECT 
            COUNT(*) as total_entregas,
            COALESCE(SUM(valor_entrega), 0) as total_ganho,
            COALESCE(SUM(distancia_km), 0) as total_km
        FROM entregas
        WHERE motoboy_id = :mid AND status = 'entregue'
    """), {"mid": st.session_state.motoboy_id})
    
    stats_row = result.mappings().fetchone()
    stats = dict(stats_row) if stats_row else {"total_entregas": 0, "total_ganho": 0.0, "total_km": 0.0}
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{stats['total_entregas']}</h2>
            <p>Entregas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h2>R$ {stats['total_ganho']:.2f}</h2>
            <p>Total Ganho</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{stats['total_km']:.1f} km</h2>
            <p>Distância</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("📜 Histórico de Entregas")
    
    result = session.execute(text("""
        SELECT e.*, p.comanda, p.cliente_nome
        FROM entregas e
        JOIN pedidos p ON e.pedido_id = p.id
        WHERE e.motoboy_id = :mid AND e.status = 'entregue'
        ORDER BY e.horario_entrega DESC
        LIMIT 20
    """), {"mid": st.session_state.motoboy_id})
    
    historico = [dict(row) for row in result.mappings().fetchall()]
    
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
                    st.markdown(f"**Data:** {entrega.get('horario_entrega', 'N/A')[:16]}")

# ==================== PERFIL ====================

def tela_perfil():
    st.title("👤 Meu Perfil")
    
    motoboy = st.session_state.motoboy_dados
    
    st.markdown(f"### {motoboy['nome']}")
    st.markdown(f"**Usuário:** {motoboy['usuario']}")
    st.markdown(f"**Telefone:** {motoboy.get('telefone', 'Não informado')}")
    st.markdown(f"**Restaurante:** {motoboy['restaurante_nome']}")
    
    st.markdown("---")
    
    st.markdown("### 📊 Estatísticas")
    st.metric("Total de Entregas", motoboy.get('total_entregas', 0))
    st.metric("Total Ganho", f"R$ {motoboy.get('total_ganhos', 0.0):.2f}")
    
    st.markdown("---")
    
    if st.button("🚪 Sair", use_container_width=True, type="primary"):
        fazer_logout()
        st.rerun()

# ==================== MENU INFERIOR ====================

def menu_inferior():
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
    verificar_login()
    
    if 'tela_atual' not in st.session_state:
        st.session_state.tela_atual = "entregas"
    
    if not st.session_state.motoboy_logado:
        if st.session_state.get('tela_atual') == "cadastro":
            tela_cadastro()
        else:
            tela_login()
    else:
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
        
        menu_inferior()

if __name__ == "__main__":
    main()