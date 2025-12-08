import streamlit as st
from supabase import create_client, Client
import time
from datetime import datetime, date

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Triagem SSVV", page_icon="🩺", layout="centered", initial_sidebar_state="collapsed")

# --- 2. CSS ---
# --- 2. CSS (ESTILO FINAL: AZUL, GRANDE E COM HOVER) ---
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

        /* --- BOTÃO PADRÃO (Entrar, Sair) --- */
        .stButton > button {
            width: 100%; height: 3.5rem; 
            font-size: 20px !important; font-weight: bold;
            border-radius: 8px; border: none;

            /* Cor Normal */
            background-color: #007bff !important; 
            color: white !important;
        }

        /* Efeito Hover (Mouse em cima) - Botão Padrão */
        .stButton > button:hover {
            background-color: #0056b3 !important; /* Azul mais escuro */
            color: white !important;
        }

        /* --- BOTÃO SALVAR (Formulário) --- */
        [data-testid="stFormSubmitButton"] > button {
            height: 3rem; 
            font-size: 20px !important;

            /* Cor Normal (Um pouco mais escura que o padrão) */
            background-color: #004494 !important; 
            color: white !important;
        }

        /* Efeito Hover (Mouse em cima) - Botão Salvar */
        [data-testid="stFormSubmitButton"] > button:hover {
            background-color: #002a5c !important; /* Azul bem escuro */
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
        if st.session_state.selectbox_nome == "Selecione...":
            st.toast("⚠️ Selecione um nome antes de salvar!")
            return

        # Prepara Dados
        dados = {
            "data_atendimento": str(st.session_state.data_atendimento),
            "registro_profissional": st.session_state.usuario['registro_profissional'],
            "nome_profissional": st.session_state.usuario['nome_profissional'],
            "voluntario_nome": st.session_state.selectbox_nome,
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
        st.toast(f"✅ Salvo: {dados['voluntario_nome']}", icon="🎉")

        # --- RESET TOTAL (AQUI ESTÁ A CORREÇÃO) ---

        # 1. Força o Selectbox a mudar o valor interno para o padrão
        st.session_state.selectbox_nome = "Selecione..."
        st.session_state.idx_nome = 0

        # 2. Limpa Números -> None
        campos_none = ["pas", "pad", "fc", "spo", "fr", "dx", "obs", "status"]
        for c in campos_none:
            if c in st.session_state: st.session_state[c] = None

        # 3. Limpa Checkboxes -> False
        campos_false = ["dormiu", "desjejum", "med_sono", "tontura", "aso", "intercor"]
        for c in campos_false:
            if c in st.session_state: st.session_state[c] = False

    except Exception as e:
        st.error(f"Erro ao salvar: {e}")


# --- 6. INICIALIZAÇÃO ---
if "logado" not in st.session_state: st.session_state["logado"] = False
if "idx_nome" not in st.session_state: st.session_state["idx_nome"] = 0

# Inicializa variaveis
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
        reg = st.text_input("Registro", placeholder="Ex: 1000")
        sen = st.text_input("Senha", type="password", placeholder="4 últimos dígitos")
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
    c1.write(f"Olá, **{st.session_state.usuario['nome_profissional']}**")
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

    st.markdown("### 👤 Identificação")
    st.date_input("Data Atendimento", value=date.today(), format="DD/MM/YYYY", key="data_atendimento")

    # O index e a Key trabalham juntos agora
    nome = st.selectbox(
        "Nome",
        ["Selecione..."] + lista,
        index=st.session_state["idx_nome"],
        key="selectbox_nome"
    )

    if nome != "Selecione...":
        d_nasc = st.session_state["dados_voluntarios"].get(nome)
        idade = calcular_idade(d_nasc)
        st.session_state["idade_temp"] = idade
        st.info(f"🎂 Idade: **{idade} anos**")

        with st.form("form_triagem"):
            st.markdown("### 🩺 Sinais Vitais")
            c1, c2, c3 = st.columns(3)
            st.number_input("PAS", 0, 300, step=1, value=None, placeholder="0", key="pas")
            st.number_input("PAD", 0, 200, step=1, value=None, placeholder="0", key="pad")
            st.number_input("FC", 0, 250, step=1, value=None, placeholder="0", key="fc")

            c4, c5, c6 = st.columns(3)
            st.number_input("SpO2", 0, 100, step=1, value=None, placeholder="0", key="spo")
            st.number_input("FR", 0, 100, step=1, value=None, placeholder="0", key="fr")
            st.number_input("Dextro", 0, 600, step=1, value=None, placeholder="0", key="dx")

            st.markdown("### ✅ Avaliação")
            col_a, col_b = st.columns(2)
            with col_a:
                st.checkbox("Dormiu bem?", key="dormiu")
                st.checkbox("Fez desjejum?", key="desjejum")
                st.checkbox("Medicação sono?", key="med_sono")
            with col_b:
                st.checkbox("Tontura?", key="tontura")
                st.checkbox("ASO em dia?", key="aso")
                st.checkbox("Intercorrência?", key="intercor")

            st.text_area("Observações", key="obs")
            st.markdown("### 🏁 Parecer")
            st.radio("Condição:", ["Apto", "Inapto"], horizontal=True, key="status")

            st.form_submit_button("💾 SALVAR REGISTRO", on_click=salvar_callback)