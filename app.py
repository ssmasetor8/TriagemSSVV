import streamlit as st
from supabase import create_client, Client
import time
from datetime import datetime, date

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Triagem SSVV", page_icon="🩺", layout="centered", initial_sidebar_state="collapsed")

# --- 2. CSS ---
st.markdown("""
    <style>
        #MainMenu {visibility: visible;} 
        footer {visibility: hidden;}
        header {visibility: hidden;} 
        .block-container {padding-top: 1rem; padding-bottom: 1rem;}

        /* --- FONTES MAIORES --- */
        html, body, p, label, .stMarkdown {
            font-size: 18px !important;
        }
        input, .stSelectbox div {
            font-size: 18px !important;
        }

        /* --- BOTÃO PADRÃO --- */
        .stButton > button {
            width: 100%; height: 3.5rem; 
            font-size: 20px !important; font-weight: bold;
            border-radius: 8px; border: none;
            background-color: #007bff !important; 
            color: white !important;
        }
        .stButton > button:hover {
            background-color: #0056b3 !important; 
            color: white !important;
        }

        /* --- BOTÃO SALVAR --- */
        [data-testid="stFormSubmitButton"] > button {
            height: 3rem; 
            font-size: 20px !important;
            background-color: #004494 !important; 
            color: white !important;
        }
        [data-testid="stFormSubmitButton"] > button:hover {
            background-color: #002a5c !important; 
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONEXÃO ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.error("❌ Erro no secrets.toml")
    st.stop()

LISTA_COMUNS = sorted([
    "Cidade Ipava", "Jardim Amália", "Jardim Ângela", "Jardim Aracati",
    "Jardim Capão Redondo", "Jardim Célia", "Jardim Das Flores",
    "Jardim Das Palmas", "Jardim Guarujá", "Jardim Ibirapuera",
    "Jardim Ingá", "Jardim Leônidas Moreira", "Jardim Lídia",
    "Jardim Nakamura", "Jardim Novo Oriente", "Jardim Piracuama",
    "Jardim São Francisco", "Jardim São Lourenço", "Jardim São Luiz",
    "Jardim Sete Lagos", "Jardim Umarizal", "Jardim Vera Cruz",
    "M'Boi Mirim", "Parque Do Lago", "Parque Fernanda",
    "Parque Maria Helena", "Parque Santo Antônio", "Piraporinha",
    "Riviera Paulista", "Vila Remo", "Vila Santa Lúcia"
])

areas_normais = sorted([
    "Manutenção", "Cozinha", "Limpeza", "Porteiros",
    "Administração", "Ministerio"
])
LISTA_AREAS = areas_normais + ["Outros"]


# --- 4. FUNÇÕES ---
def tentar_login(registro, senha):
    try:
        resp = supabase.table("tabela_profissional").select("*").eq("registro_profissional", registro).execute()
        if resp.data:
            user = resp.data[0]
            if senha == str(user['registro_profissional'])[-4:]:
                return user
    except:
        pass
    return None


def calcular_idade(data_nasc_str):
    if not data_nasc_str: return 0
    try:
        nasc = datetime.strptime(data_nasc_str, "%Y-%m-%d").date()
        hoje = date.today()
        return hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
    except:
        return 0


# --- 5. O GATILHO DE SALVAR (Callback) ---
def salvar_callback():
    try:
        # Validações
        if st.session_state.selectbox_nome == "Selecione...":
            st.toast("⚠️ Selecione um VOLUNTÁRIO!", icon="⚠️")
            return

        if st.session_state.selectbox_comum == "Selecione...":
            st.toast("⚠️ Selecione a CASA DE ORAÇÃO!", icon="⚠️")
            return

        if st.session_state.selectbox_area == "Selecione...":
            st.toast("⚠️ Selecione a ÁREA/SETOR!", icon="⚠️")
            return

        # Prepara Dados
        dados = {
            "data_atendimento": str(st.session_state.data_atendimento),
            "registro_profissional": st.session_state.usuario['registro_profissional'],
            "nome_profissional": st.session_state.usuario['nome_profissional'],

            "casa_oracao": st.session_state.selectbox_comum,
            "voluntario_nome": st.session_state.selectbox_nome,
            "area_voluntario": st.session_state.selectbox_area,
            "idade_voluntario": st.session_state.get("idade_temp", 0),

            "pas": st.session_state.pas, "pad": st.session_state.pad, "fc": st.session_state.fc,
            "spo": st.session_state.spo, "fr": st.session_state.fr, "dextro": st.session_state.dx,

            "dormiu_bem": st.session_state.dormiu, "desjejum": st.session_state.desjejum,
            "medicacao_sono": st.session_state.med_sono, "tontura": st.session_state.tontura,
            "aso": st.session_state.aso, "intercorrencia": st.session_state.intercor,

            "descricao_intercorrencia": st.session_state.obs,
            "parecer": (True if st.session_state.status == "Apto" else False)
        }

        # Salva
        supabase.table("tabela_registros").insert(dados).execute()
        st.toast(f"Salvo: {dados['voluntario_nome']}", icon="✅")

        # --- RESET INTELIGENTE ---

        st.session_state.idx_nome = 0
        st.session_state.idx_area = 0  # Reseta a área

        # Força atualização visual
        st.session_state.selectbox_nome = "Selecione..."
        st.session_state.selectbox_area = "Selecione..."

        # Limpa Números
        campos_none = ["pas", "pad", "fc", "spo", "fr", "dx", "obs", "status"]
        for c in campos_none:
            if c in st.session_state: st.session_state[c] = None

        # Limpa Checkboxes
        campos_false = ["dormiu", "desjejum", "med_sono", "tontura", "aso", "intercor"]
        for c in campos_false:
            if c in st.session_state: st.session_state[c] = False

    except Exception as e:
        st.error(f"Erro ao salvar: {e}")


# --- 6. INICIALIZAÇÃO ---
if "logado" not in st.session_state: st.session_state["logado"] = False

# Índices
if "idx_nome" not in st.session_state: st.session_state["idx_nome"] = 0
if "idx_area" not in st.session_state: st.session_state["idx_area"] = 0

# Persistente
if "selectbox_comum" not in st.session_state: st.session_state["selectbox_comum"] = "Selecione..."

# Form Fields
numeros = ["pas", "pad", "fc", "spo", "fr", "dx", "obs", "status"]
checks = ["dormiu", "desjejum", "med_sono", "tontura", "aso", "intercor"]
for k in numeros:
    if k not in st.session_state: st.session_state[k] = None
for k in checks:
    if k not in st.session_state: st.session_state[k] = False

# --- 7. TELA ---
if not st.session_state["logado"]:
    st.markdown("<h1 style='text-align: center;'>🩺 Triagem SSVV</h1>", unsafe_allow_html=True)
    st.divider()
    with st.container():
        reg = st.text_input("Registro")
        sen = st.text_input("Senha", type="password")
        if st.button("ENTRAR"):
            user = tentar_login(reg, sen)
            if user:
                st.session_state.logado = True
                st.session_state.usuario = user
                st.rerun()
            else:
                st.error("Inválido.")
else:
    c1, c2 = st.columns([3, 1])
    c1.write(f"Olá, **{st.session_state.usuario['nome_profissional']}**, a paz de Deus !!!")
    if c2.button("Sair"):
        st.session_state.logado = False
        st.rerun()
    st.divider()

    if "dados_voluntarios" not in st.session_state:
        try:
            resp = supabase.table("tabela_voluntario").select("voluntario_nome, data_nascimento").execute()
            st.session_state["dados_voluntarios"] = {d['voluntario_nome']: d['data_nascimento'] for d in resp.data}
        except:
            st.session_state["dados_voluntarios"] = {}

    lista = sorted(list(st.session_state["dados_voluntarios"].keys()))

    st.markdown("### 👷‍♂️️ Identificação Voluntário")

    # 1. Data
    st.date_input("Data Atendimento", value=date.today(), format="DD/MM/YYYY", key="data_atendimento")

    # 2. Casa de Oração
    st.selectbox("Casa de Oração", ["Selecione..."] + LISTA_COMUNS, key="selectbox_comum")

    # 3. Nome
    nome = st.selectbox(
        "Nome Voluntário",
        ["Selecione..."] + lista,
        index=st.session_state["idx_nome"],
        key="selectbox_nome"
    )

    # --- CONDIÇÃO: SÓ MOSTRA SELECIONAR NOME ---
    if nome != "Selecione...":
        # 4. Área/Setor (Agora aparece aqui dentro)
        st.selectbox(
            "Área / Setor",
            ["Selecione..."] + LISTA_AREAS,
            index=st.session_state["idx_area"],
            key="selectbox_area"
        )

        d_nasc = st.session_state["dados_voluntarios"].get(nome)
        idade = calcular_idade(d_nasc)
        st.session_state["idade_temp"] = idade
        st.info(f"🎂 Idade Voluntário: **{idade} anos**")

        with st.form("form_triagem"):
            st.markdown("### 🩺 Sinais Vitais")
            c1, c2, c3 = st.columns(3)
            st.number_input("PA (PAS)", 0, 300, step=1, value=None, placeholder="ex.120", key="pas")
            st.number_input("PAD (PAD)", 0, 200, step=1, value=None, placeholder="ex.80", key="pad")
            st.number_input("Freq. Cardíaca (bpm)", 0, 250, step=1, value=None, placeholder="ex.70", key="fc")

            c4, c5, c6 = st.columns(3)
            st.number_input("Saturação (SpO2)", 0, 100, step=1, value=None, placeholder="ex.96", key="spo")
            st.number_input("Freq. Respiratória", 0, 100, step=1, value=None, placeholder="ex.22", key="fr")
            st.number_input("Dextro", 0, 600, step=1, value=None, placeholder="ex.120", key="dx")

            st.markdown("### 📋 Avaliação")
            col_a, col_b = st.columns(2)
            with col_a:
                st.checkbox("Dormiu bem?", key="dormiu")
                st.checkbox("Fez desjejum?", key="desjejum")
                st.checkbox("Usa medicação que causa sono?", key="med_sono")
            with col_b:
                st.checkbox("Tontura, dor de cabeça, mal estar ?", key="tontura")
                st.checkbox("ASO em dia?", key="aso")
                st.checkbox("Intercorrência na Triagem?", key="intercor")

            st.text_area("Observações Gerais", key="obs")
            st.markdown("### 👩‍⚕️ Parecer")
            st.radio("Condição:", ["Apto", "Inapto"], horizontal=True, key="status")

            st.form_submit_button("💾 SALVAR REGISTRO", on_click=salvar_callback)