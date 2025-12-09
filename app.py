# import streamlit as st
# from supabase import create_client, Client
# import time
# from datetime import datetime, date
# import csv
# import io
#
# # --- 1. CONFIGURAÇÃO ---
# st.set_page_config(page_title="Triagem SSVV", page_icon="🩺", layout="centered", initial_sidebar_state="collapsed")
#
# # --- 2. CSS ---
# st.markdown("""
#     <style>
#         #MainMenu {visibility: visible;}
#         footer {visibility: hidden;}
#         header {visibility: hidden;}
#         .block-container {padding-top: 1rem; padding-bottom: 1rem;}
#
#         /* --- FONTES MAIORES --- */
#         html, body, p, label, .stMarkdown {
#             font-size: 20px !important;
#         }
#         input, .stSelectbox div {
#             font-size: 20px !important;
#         }
#
#         /* --- BOTÃO PADRÃO --- */
#         .stButton > button {
#             width: 100%; height: 3.5rem;
#             font-size: 20px !important; font-weight: bold;
#             border-radius: 8px; border: none;
#             background-color: #007bff !important;
#             color: white !important;
#         }
#         .stButton > button:hover {
#             background-color: #0056b3 !important;
#             color: white !important;
#         }
#
#         /* --- BOTÃO SALVAR --- */
#         [data-testid="stFormSubmitButton"] > button {
#             height: 3rem;
#             font-size: 20px !important;
#             background-color: #004494 !important;
#             color: white !important;
#         }
#         [data-testid="stFormSubmitButton"] > button:hover {
#             background-color: #002a5c !important;
#             color: white !important;
#         }
#     </style>
# """, unsafe_allow_html=True)
#
# # --- 3. CONEXÃO ---
# try:
#     url = st.secrets["SUPABASE_URL"]
#     key = st.secrets["SUPABASE_KEY"]
#     supabase: Client = create_client(url, key)
# except:
#     st.error("❌ Erro no secrets.toml")
#     st.stop()
#
# # --- LISTAS ---
# LISTA_COMUNS = sorted([
#     "Cidade Ipava", "Jardim Amália", "Jardim Ângela", "Jardim Aracati",
#     "Jardim Capão Redondo", "Jardim Célia", "Jardim Das Flores",
#     "Jardim Das Palmas", "Jardim Guarujá", "Jardim Ibirapuera",
#     "Jardim Ingá", "Jardim Leônidas Moreira", "Jardim Lídia",
#     "Jardim Nakamura", "Jardim Novo Oriente", "Jardim Piracuama",
#     "Jardim São Francisco", "Jardim São Lourenço", "Jardim São Luiz",
#     "Jardim Sete Lagos", "Jardim Umarizal", "Jardim Vera Cruz",
#     "M'Boi Mirim", "Parque Do Lago", "Parque Fernanda",
#     "Parque Maria Helena", "Parque Santo Antônio", "Piraporinha",
#     "Riviera Paulista", "Vila Remo", "Vila Santa Lúcia"
# ])
#
# areas_normais = sorted([
#     "Manutenção", "Cozinha", "Limpeza", "Porteiros",
#     "Administração",
# ])
# LISTA_AREAS = areas_normais + ["Outros"]
#
#
# # --- 4. FUNÇÕES GERAIS ---
# def tentar_login(registro, senha):
#     try:
#         resp = supabase.table("tabela_profissional").select("*").eq("registro_profissional", registro).execute()
#         if resp.data:
#             user = resp.data[0]
#             if senha == str(user['registro_profissional'])[-4:]:
#                 return user
#     except:
#         pass
#     return None
#
#
# def calcular_idade(data_nasc_str):
#     if not data_nasc_str: return 0
#     try:
#         nasc = datetime.strptime(data_nasc_str, "%Y-%m-%d").date()
#         hoje = date.today()
#         return hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
#     except:
#         return 0
#
#
# def gerar_csv_corrigido():
#     """Gera CSV compatível com Excel Brasil"""
#     try:
#         resp = supabase.table("tabela_registros").select("*").order("id", desc=True).execute()
#         dados = resp.data
#         if not dados: return None
#
#         output = io.StringIO()
#         writer = csv.DictWriter(output, fieldnames=dados[0].keys(), delimiter=';')
#         writer.writeheader()
#         writer.writerows(dados)
#         return output.getvalue().encode('utf-8-sig')
#     except Exception as e:
#         st.error(f"Erro CSV: {e}")
#         return None
#
#
# # --- CALLBACKS DE CADASTRO (GESTOR) ---
# def cadastrar_voluntario_callback():
#     nome = st.session_state.novo_vol_nome
#     nasc = st.session_state.novo_vol_nasc
#     if not nome:
#         st.toast("Preencha o nome!", icon="⚠️")
#         return
#     try:
#         dados = {"voluntario_nome": nome, "data_nascimento": str(nasc)}
#         supabase.table("tabela_voluntario").insert(dados).execute()
#         st.toast(f"Cadastrado: {nome}", icon="✅")
#         if "dados_voluntarios" in st.session_state: del st.session_state["dados_voluntarios"]
#         st.session_state.novo_vol_nome = ""
#     except Exception as e:
#         st.error(f"Erro: {e}")
#
#
# def cadastrar_profissional_callback():
#     reg = st.session_state.novo_prof_reg
#     nome = st.session_state.novo_prof_nome
#     admin_bool = st.session_state.novo_prof_admin
#     if not reg or not nome:
#         st.toast("Preencha Registro e Nome!", icon="⚠️")
#         return
#     try:
#         dados = {
#             "registro_profissional": reg,
#             "nome_profissional": nome,
#             "admin": admin_bool
#         }
#         supabase.table("tabela_profissional").insert(dados).execute()
#         st.toast(f"Profissional {nome} cadastrado!", icon="✅")
#         st.session_state.novo_prof_reg = ""
#         st.session_state.novo_prof_nome = ""
#         st.session_state.novo_prof_admin = False
#     except Exception as e:
#         st.error(f"Erro: {e}")
#
#
# # --- 5. O GATILHO DE SALVAR (Callback com Validação) ---
# def salvar_callback():
#     try:
#         # --- VALIDAÇÕES ---
#         if st.session_state.selectbox_comum == "Selecione...":
#             st.toast("⚠️ Selecione a CASA DE ORAÇÃO!", icon="🛑")
#             return
#         if st.session_state.selectbox_nome == "Selecione...":
#             st.toast("⚠️ Selecione um VOLUNTÁRIO!", icon="🛑")
#             return
#         if st.session_state.selectbox_area == "Selecione...":
#             st.toast("⚠️ Selecione a ÁREA/SETOR!", icon="🛑")
#             return
#
#         # Travas de Obrigatórios
#         if st.session_state.pas is None or st.session_state.pad is None:
#             st.toast("⚠️ A Pressão Arterial (PAS/PAD) é obrigatória!", icon="🛑")
#             return
#         if st.session_state.fc is None:
#             st.toast("⚠️ A Frequência Cardíaca é obrigatória!", icon="🛑")
#             return
#         if st.session_state.spo is None:
#             st.toast("⚠️ A Saturação (SpO2) é obrigatória!", icon="🛑")
#             return
#         if st.session_state.status is None:
#             st.toast("⚠️ Selecione se está APTO ou INAPTO!", icon="🛑")
#             return
#
#         # --- PREPARAÇÃO DOS DADOS ---
#         dados = {
#             "data_atendimento": str(st.session_state.data_atendimento),
#             "registro_profissional": st.session_state.usuario['registro_profissional'],
#             "nome_profissional": st.session_state.usuario['nome_profissional'],
#
#             "casa_oracao": st.session_state.selectbox_comum,
#             "voluntario_nome": st.session_state.selectbox_nome,
#             "area_voluntario": st.session_state.selectbox_area,
#             "idade_voluntario": st.session_state.get("idade_temp", 0),
#
#             "pas": st.session_state.pas, "pad": st.session_state.pad, "fc": st.session_state.fc,
#             "spo": st.session_state.spo, "fr": st.session_state.fr, "dextro": st.session_state.dx,
#
#             "dormiu_bem": st.session_state.dormiu, "desjejum": st.session_state.desjejum,
#             "medicacao_sono": st.session_state.med_sono, "tontura": st.session_state.tontura,
#             "aso": st.session_state.aso, "intercorrencia": st.session_state.intercor,
#
#             "descricao_intercorrencia": st.session_state.obs,
#             "parecer": (True if st.session_state.status == "Apto" else False)
#         }
#
#         # --- SALVAR ---
#         supabase.table("tabela_registros").insert(dados).execute()
#         st.toast(f"✅ Salvo com sucesso: {dados['voluntario_nome']}", icon="💾")
#
#         # --- RESET ---
#         st.session_state.idx_nome = 0
#         st.session_state.idx_area = 0
#         st.session_state.selectbox_nome = "Selecione..."
#         st.session_state.selectbox_area = "Selecione..."
#
#         campos_none = ["pas", "pad", "fc", "spo", "fr", "dx", "obs", "status"]
#         for c in campos_none:
#             if c in st.session_state: st.session_state[c] = None
#
#         campos_false = ["dormiu", "desjejum", "med_sono", "tontura", "aso", "intercor"]
#         for c in campos_false:
#             if c in st.session_state: st.session_state[c] = False
#
#     except Exception as e:
#         st.error(f"Erro ao salvar: {e}")
#
#
# # --- 6. INICIALIZAÇÃO ---
# if "logado" not in st.session_state: st.session_state["logado"] = False
# if "pagina_gestor" not in st.session_state: st.session_state["pagina_gestor"] = False
#
# # Índices
# if "idx_nome" not in st.session_state: st.session_state["idx_nome"] = 0
# if "idx_area" not in st.session_state: st.session_state["idx_area"] = 0
# if "selectbox_comum" not in st.session_state: st.session_state["selectbox_comum"] = "Selecione..."
#
# # Form Fields
# numeros = ["pas", "pad", "fc", "spo", "fr", "dx", "obs", "status"]
# checks = ["dormiu", "desjejum", "med_sono", "tontura", "aso", "intercor"]
# for k in numeros:
#     if k not in st.session_state: st.session_state[k] = None
# for k in checks:
#     if k not in st.session_state: st.session_state[k] = False
#
# # --- 7. TELA ---
#
# # === TELA 1: LOGIN ===
# if not st.session_state["logado"]:
#     st.markdown("<h1 style='text-align: center;'>🩺 Triagem SSVV</h1>", unsafe_allow_html=True)
#     st.divider()
#     with st.container():
#         reg = st.text_input("Registro")
#         sen = st.text_input("Senha", type="password")
#         if st.button("Entrar"):
#             user = tentar_login(reg, sen)
#             if user:
#                 st.session_state.logado = True
#                 st.session_state.usuario = user
#                 st.rerun()
#             else:
#                 st.error("Inválido.")
#
# # === TELA 2: ÁREA LOGADA ===
# else:
#     is_admin = st.session_state.usuario.get('admin', False)
#
#     if is_admin:
#         c1, c2, c3 = st.columns([2, 1, 1])
#     else:
#         c1, c3 = st.columns([3, 1])
#
#     with c1:
#         st.write(f"Olá, **{st.session_state.usuario['nome_profissional']}**, a paz de Deus !!!")
#
#     if is_admin:
#         with c2:
#             if st.button("⚙️ Gestor"):
#                 st.session_state.pagina_gestor = True
#                 st.rerun()
#
#     with c3:
#         if st.button("⬅️ Sair"):
#             st.session_state.logado = False
#             st.session_state.pagina_gestor = False
#             st.rerun()
#
#     st.divider()
#
#     # === SUB-TELA: PAINEL GESTOR ===
#     if st.session_state["pagina_gestor"]:
#         st.markdown("## ⚙️ Painel do Gestor")
#         if st.button("⬅️ Voltar"):
#             st.session_state.pagina_gestor = False
#             st.rerun()
#
#         tab1, tab2, tab3 = st.tabs(["🆕 Voluntários", "🏥 Profissionais", "📥 Relatórios"])
#
#         with tab1:
#             st.text_input("Nome Completo", key="novo_vol_nome")
#             st.date_input("Data Nascimento", value=date(1990, 1, 1), format="DD/MM/YYYY", key="novo_vol_nasc")
#             # ADICIONEI KEY UNICA AQUI PARA CORRIGIR O ERRO
#             st.button("Cadastrar", on_click=cadastrar_voluntario_callback, key="btn_cad_vol")
#
#         with tab2:
#             st.text_input("Registro (Somente números)", key="novo_prof_reg")
#             st.text_input("Nome do Profissional", key="novo_prof_nome")
#             st.checkbox("É Administrador?", key="novo_prof_admin")
#             # ADICIONEI KEY UNICA AQUI TAMBEM
#             st.button("Cadastrar", on_click=cadastrar_profissional_callback, key="btn_cad_prof")
#
#         with tab3:
#             st.info("Baixe a planilha completa.")
#             csv_data = gerar_csv_corrigido()
#             if csv_data:
#                 hoje = datetime.now().strftime("%d-%m-%Y_%Hh%M")
#                 st.download_button(
#                     label="📥 Baixar Planilha (Excel)",
#                     data=csv_data,
#                     file_name=f"triagem_{hoje}.csv",
#                     mime="text/csv"
#                 )
#
#     # === SUB-TELA: TRIAGEM (A ORIGINAL) ===
#     else:
#         if "dados_voluntarios" not in st.session_state:
#             try:
#                 resp = supabase.table("tabela_voluntario").select("voluntario_nome, data_nascimento").execute()
#                 st.session_state["dados_voluntarios"] = {d['voluntario_nome']: d['data_nascimento'] for d in resp.data}
#             except:
#                 st.session_state["dados_voluntarios"] = {}
#
#         lista = sorted(list(st.session_state["dados_voluntarios"].keys()))
#
#         st.markdown("### 👷‍♂️️ Identificação Voluntário")
#
#         st.date_input("Data Atendimento", value=date.today(), format="DD/MM/YYYY", key="data_atendimento")
#         st.selectbox("Casa de Oração", ["Selecione..."] + LISTA_COMUNS, key="selectbox_comum")
#
#         nome = st.selectbox(
#             "Nome Voluntário",
#             ["Selecione..."] + lista,
#             index=st.session_state["idx_nome"],
#             key="selectbox_nome"
#         )
#
#         if nome != "Selecione...":
#             st.selectbox(
#                 "Área / Setor",
#                 ["Selecione..."] + LISTA_AREAS,
#                 index=st.session_state["idx_area"],
#                 key="selectbox_area"
#             )
#
#             d_nasc = st.session_state["dados_voluntarios"].get(nome)
#             idade = calcular_idade(d_nasc)
#             st.session_state["idade_temp"] = idade
#             st.info(f"🎂 Idade Voluntário: **{idade} anos**")
#
#             with st.form("form_triagem"):
#                 st.markdown("### 🩺 Sinais Vitais")
#                 c1, c2, c3 = st.columns(3)
#                 st.number_input("PA (PAS) *", 0, 300, step=1, value=None, placeholder="ex. 120", key="pas")
#                 st.number_input("PA (PAD) *", 0, 200, step=1, value=None, placeholder="ex. 80", key="pad")
#                 st.number_input("Freq. Cardíaca (bpm) *", 0, 250, step=1, value=None, placeholder="ex. 70", key="fc")
#
#                 c4, c5, c6 = st.columns(3)
#                 st.number_input("Saturação (SpO2) *", 0, 100, step=1, value=None, placeholder="ex. 96", key="spo")
#                 st.number_input("Freq. Respiratória", 0, 100, step=1, value=None, placeholder="ex. 22", key="fr")
#                 st.number_input("Dextro", 0, 600, step=1, value=None, placeholder="ex. 120", key="dx")
#
#                 st.markdown("### 📋 Avaliação")
#                 col_a, col_b = st.columns(2)
#                 with col_a:
#                     st.checkbox("Dormiu bem?", key="dormiu")
#                     st.checkbox("Fez desjejum?", key="desjejum")
#                     st.checkbox("Uso de medicação que causa sono?", key="med_sono")
#                 with col_b:
#                     st.checkbox("Tontura, dor de cabeça, mal estar ?", key="tontura")
#                     st.checkbox("ASO em dia (vigente)?", key="aso")
#                     st.checkbox("Intercorrência na Triagem?", key="intercor")
#
#                 st.text_area("Descrever Intercorrencia / Observações", key="obs")
#
#                 st.markdown("### 👩‍⚕️ Parecer")
#                 st.radio("Condição para Atuação: *", ["Apto", "Inapto"], index=None, horizontal=True, key="status")
#
#                 st.form_submit_button("💾 Salvar Registro", on_click=salvar_callback)

import streamlit as st
from supabase import create_client, Client
import time
from datetime import datetime, date
import csv
import io

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Triagem SSVV", page_icon="🩺", layout="centered", initial_sidebar_state="collapsed")

#--- 2. CSS
# --- 2. CSS (A SOLUÇÃO AGRESSIVA PARA O CONTRASTE) ---
st.markdown("""
    <style>
        #MainMenu {visibility: visible;} 
        footer {visibility: hidden;}
        header {visibility: hidden;} 
        .block-container {padding-top: 1rem; padding-bottom: 5rem;}

        /* --- FONTES MAIORES --- */
        html, body, p, label, .stMarkdown {
            font-size: 18px !important;
        }

        /* --- COR DE FUNDO AZUL PETRÓLEO (Final) --- */
        body { 
            background-color: #0D2C50 !important; /* Fundo do Corpo do App */
        }

        /* --- FIX: SELECTBOX TEIMOSO (Targeting the UL List) --- */
        /* Garante que o container flutuante e a lista de opções fiquem Petróleo */
        div[data-baseweb="popover"] {
            background-color: #042A4A !important; /* Azul Petróleo Forte */
            border: none !important;
        }
        div[data-baseweb="popover"] > div > ul {
            background-color: #042A4A !important; /* Targeta a UL que segura a lista */
            color: white !important;
        }

        /* Garante que o texto de input e opções sejam brancos/azuis claros */
        input, .stSelectbox div {
            font-size: 18px !important;
            color: #63b3ed !important; 
        }

        /* Garante a cor de seleção quando o mouse passa */
        div[data-baseweb="popover"] div[role="option"] {
            color: white !important;
        }
        div[data-baseweb="popover"] div[role="option"]:hover {
            background-color: #004494 !important; /* Azul escuro no hover */
        }

        /* --- BOTÕES E LAYOUT --- (Mantidos)
        .stButton > button { ... }
        [data-testid="stFormSubmitButton"] > button { ... }
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

# --- LISTAS ---
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
    "Administração",
])
LISTA_AREAS = areas_normais + ["Outros"]


# --- 4. FUNÇÕES GERAIS ---
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


def gerar_csv_corrigido():
    try:
        resp = supabase.table("tabela_registros").select("*").order("id", desc=True).execute()
        dados = resp.data
        if not dados: return None
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=dados[0].keys(), delimiter=';')
        writer.writeheader()
        writer.writerows(dados)
        return output.getvalue().encode('utf-8-sig')
    except Exception as e:
        st.error(f"Erro CSV: {e}")
        return None


# --- CALLBACKS ---
def cadastrar_voluntario_callback():
    nome = st.session_state.novo_vol_nome
    nasc = st.session_state.novo_vol_nasc
    if not nome:
        st.toast("Preencha o nome!", icon="⚠️")
        return
    try:
        dados = {"voluntario_nome": nome, "data_nascimento": str(nasc)}
        supabase.table("tabela_voluntario").insert(dados).execute()
        st.toast(f"Cadastrado: {nome}", icon="✅")
        if "dados_voluntarios" in st.session_state: del st.session_state["dados_voluntarios"]
        st.session_state.novo_vol_nome = ""
    except Exception as e:
        st.error(f"Erro: {e}")


def cadastrar_profissional_callback():
    reg = st.session_state.novo_prof_reg
    nome = st.session_state.novo_prof_nome
    admin_bool = st.session_state.novo_prof_admin
    if not reg or not nome:
        st.toast("Preencha Registro e Nome!", icon="⚠️")
        return
    try:
        dados = {"registro_profissional": reg, "nome_profissional": nome, "admin": admin_bool}
        supabase.table("tabela_profissional").insert(dados).execute()
        st.toast(f"Profissional {nome} cadastrado!", icon="✅")
        st.session_state.novo_prof_reg = ""
        st.session_state.novo_prof_nome = ""
        st.session_state.novo_prof_admin = False
    except Exception as e:
        st.error(f"Erro: {e}")


def salvar_callback():
    try:
        if st.session_state.selectbox_comum == "Selecione...":
            st.toast("⚠️ Selecione a CASA DE ORAÇÃO!", icon="🛑")
            return
        if st.session_state.selectbox_nome == "Selecione...":
            st.toast("⚠️ Selecione um VOLUNTÁRIO!", icon="🛑")
            return
        if st.session_state.selectbox_area == "Selecione...":
            st.toast("⚠️ Selecione a ÁREA/SETOR!", icon="🛑")
            return
        if st.session_state.pas is None or st.session_state.pad is None:
            st.toast("⚠️ Pressão Arterial obrigatória!", icon="🛑")
            return
        if st.session_state.fc is None:
            st.toast("⚠️ Frequência Cardíaca obrigatória!", icon="🛑")
            return
        if st.session_state.spo is None:
            st.toast("⚠️ Saturação obrigatória!", icon="🛑")
            return
        if st.session_state.status is None:
            st.toast("⚠️ Selecione o PARECER!", icon="🛑")
            return

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

        supabase.table("tabela_registros").insert(dados).execute()
        st.toast(f"✅ Salvo: {dados['voluntario_nome']}", icon="🎉")

        # Reset
        st.session_state.idx_nome = 0
        st.session_state.idx_area = 0
        st.session_state.selectbox_nome = "Selecione..."
        st.session_state.selectbox_area = "Selecione..."

        campos_none = ["pas", "pad", "fc", "spo", "fr", "dx", "obs", "status"]
        for c in campos_none:
            if c in st.session_state: st.session_state[c] = None
        campos_false = ["dormiu", "desjejum", "med_sono", "tontura", "aso", "intercor"]
        for c in campos_false:
            if c in st.session_state: st.session_state[c] = False

    except Exception as e:
        st.error(f"Erro ao salvar: {e}")


# --- 6. INICIALIZAÇÃO ---
if "logado" not in st.session_state: st.session_state["logado"] = False
if "pagina_gestor" not in st.session_state: st.session_state["pagina_gestor"] = False
if "idx_nome" not in st.session_state: st.session_state["idx_nome"] = 0
if "idx_area" not in st.session_state: st.session_state["idx_area"] = 0
if "selectbox_comum" not in st.session_state: st.session_state["selectbox_comum"] = "Selecione..."

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
        if st.button("Entrar"):
            user = tentar_login(reg, sen)
            if user:
                st.session_state.logado = True
                st.session_state.usuario = user
                st.rerun()
            else:
                st.error("Inválido.")
else:
    # --- CABEÇALHO REFORMULADO (Mobile Friendly) ---
    is_admin = st.session_state.usuario.get('admin', False)

    # 1. Saudação em Linha Única
    st.write(f"Olá, **{st.session_state.usuario['nome_profissional']}**, a paz de Deus !!!")

    # 2. Botões em Linha Separada (50% / 50%)
    if is_admin:
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("⚙️ Gestor"):
                st.session_state.pagina_gestor = True
                st.rerun()
        with c_btn2:
            if st.button("⬅️ Sair"):
                st.session_state.logado = False
                st.session_state.pagina_gestor = False
                st.rerun()
    else:
        # Se não for admin, botão Sair ocupa largura total
        if st.button("⬅️ Sair"):
            st.session_state.logado = False
            st.rerun()

    st.divider()

    if st.session_state["pagina_gestor"]:
        st.markdown("## ⚙️ Painel do Gestor")
        if st.button("⬅️ Voltar"):
            st.session_state.pagina_gestor = False
            st.rerun()
        tab1, tab2, tab3 = st.tabs(["🆕 Voluntários", "🏥 Profissionais", "📥 Relatórios"])

        with tab1:
            st.text_input("Nome Completo", key="novo_vol_nome")
            st.date_input("Data Nascimento", value=date(1990, 1, 1), format="DD/MM/YYYY", key="novo_vol_nasc")
            st.button("Cadastrar", on_click=cadastrar_voluntario_callback, key="btn_cad_vol")
        with tab2:
            st.text_input("Registro (Somente números)", key="novo_prof_reg")
            st.text_input("Nome do Profissional", key="novo_prof_nome")
            st.checkbox("É Administrador?", key="novo_prof_admin")
            st.button("Cadastrar", on_click=cadastrar_profissional_callback, key="btn_cad_prof")
        with tab3:
            st.info("Baixe a planilha completa.")
            csv_data = gerar_csv_corrigido()
            if csv_data:
                hoje = datetime.now().strftime("%d-%m-%Y_%Hh%M")
                st.download_button(label="📥 Baixar Planilha", data=csv_data, file_name=f"triagem_{hoje}.csv",
                                   mime="text/csv")

    else:
        if "dados_voluntarios" not in st.session_state:
            try:
                resp = supabase.table("tabela_voluntario").select("voluntario_nome, data_nascimento").execute()
                st.session_state["dados_voluntarios"] = {d['voluntario_nome']: d['data_nascimento'] for d in resp.data}
            except:
                st.session_state["dados_voluntarios"] = {}

        lista = sorted(list(st.session_state["dados_voluntarios"].keys()))

        st.markdown("### 👷‍♂️️ Identificação Voluntário")
        st.date_input("Data Atendimento", value=date.today(), format="DD/MM/YYYY", key="data_atendimento")
        st.selectbox("Casa de Oração", ["Selecione..."] + LISTA_COMUNS, key="selectbox_comum")
        nome = st.selectbox("Nome Voluntário", ["Selecione..."] + lista, index=st.session_state["idx_nome"],
                            key="selectbox_nome")

        if nome != "Selecione...":
            st.selectbox("Área / Setor", ["Selecione..."] + LISTA_AREAS, index=st.session_state["idx_area"],
                         key="selectbox_area")
            d_nasc = st.session_state["dados_voluntarios"].get(nome)
            idade = calcular_idade(d_nasc)
            st.session_state["idade_temp"] = idade
            st.info(f"🎂 Idade Voluntário: **{idade} anos**")

            with st.form("form_triagem"):
                st.markdown("### 🩺 Sinais Vitais")

                # --- LAYOUT VERTICAL PARA MOBILE (Um embaixo do outro) ---
                # Removi as colunas (c1, c2, c3). Agora cada um ocupa 100% da largura.

                st.number_input("PA (PAS) *", 0, 300, step=1, value=None, placeholder="120", key="pas")
                st.number_input("PA (PAD) *", 0, 200, step=1, value=None, placeholder="80", key="pad")

                st.number_input("FC (bpm) *", 0, 250, step=1, value=None, placeholder="70", key="fc")
                st.number_input("SpO2 (%) *", 0, 100, step=1, value=None, placeholder="98", key="spo")

                st.number_input("Freq. Resp.", 0, 100, step=1, value=None, placeholder="18", key="fr")
                st.number_input("Dextro", 0, 600, step=1, value=None, placeholder="100", key="dx")

                st.markdown("### 📋 Avaliação")

                # Checkboxes também em lista vertical simples
                st.checkbox("Dormiu bem?", key="dormiu")
                st.checkbox("Fez desjejum?", key="desjejum")
                st.checkbox("Uso de medicação (sono)?", key="med_sono")
                st.checkbox("Tontura/Dor de cabeça?", key="tontura")
                st.checkbox("ASO em dia?", key="aso")
                st.checkbox("Intercorrência?", key="intercor")

                st.text_area("Observações", key="obs")
                st.markdown("### 👩‍⚕️ Parecer")
                st.radio("Condição: *", ["Apto", "Inapto"], index=None, horizontal=True, key="status")

                st.form_submit_button("💾 Salvar Registro", on_click=salvar_callback)