import os
import base64
from pathlib import Path
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv  # <--- NUEVA LIBRERÍA

# ---------- 🔑 CARGA DE VARIABLES DE ENTORNO 🔑 ----------
# Esto busca el archivo .env y carga las variables en el sistema
load_dotenv()
MI_API_KEY = os.getenv("OPENAI_API_KEY")
# --------------------------------------------------------

# ---------- DEFINICIÓN DE RUTAS ----------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
MD_PATH = DATA_DIR / "Política y Procedimiento Personas - Beneficios.2025.md"

LOGO_PATH = ASSETS_DIR / "0.png" 
AVATAR_FILENAME = "gia-topo.png"
AVATAR_PATH = ASSETS_DIR / AVATAR_FILENAME
USER_AVATAR_PATH = ASSETS_DIR / "imagen-user.png"

# ---------- CONFIGURACIÓN DE PÁGINA ----------
st.set_page_config(
    page_title="GIA - GeoInnova",
    page_icon=str(AVATAR_PATH) if AVATAR_PATH.exists() else "🤖",
    layout="centered"
)

# CSS Personalizado
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
    }
    div[data-testid="stChatInput"] {
        position: fixed; bottom: 0; width: 100%; padding: 1rem 5rem;
        background: white; z-index: 100; left: 0; right: 0;
    }
    .header-container {
        display: flex; flex-direction: row; align-items: center;
        justify-content: center; gap: 15px; margin-bottom: 10px;
    }
    .header-title {
        font-size: 2.5rem; font-weight: 700; margin: 0; color: #0F1111;
    }
    .header-logo {
        height: 60px; width: auto; /* Controla el tamaño del logo del título */
    }
    .subtitle {
        text-align: center; color: #666; font-size: 1.1rem; margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------- HEADER (LOGO GEOINNOVA + TÍTULO) ----------
def get_image_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return None

# Aquí usamos LOGO_PATH (0.png)
img_b64 = get_image_base64(LOGO_PATH)

if img_b64:
    st.markdown(f"""
    <div class="header-container">
        <img src="data:image/png;base64,{img_b64}" class="header-logo" alt="Logo GeoInnova">
        <h1 class="header-title">GIA - GeoInnova</h1>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align: center;'>🤖 GIA - GeoInnova</h1>", unsafe_allow_html=True)

st.markdown("<div class='subtitle'>Hola, soy <b>GIA</b>. Pregúntame lo que necesites sobre la empresa.</div>", unsafe_allow_html=True)

# ---------- LÓGICA DE DATOS ----------
@st.cache_data
def cargar_conocimiento_md(filepath):
    if not filepath.exists(): return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e: return f"Error: {e}"

CONOCIMIENTO_BASE = cargar_conocimiento_md(MD_PATH)

if not CONOCIMIENTO_BASE:
    st.error(f"⚠️ No se encontró el archivo Markdown en: {MD_PATH}")
    st.stop()

def answer_query(prompt: str):
    # Ya no necesitamos os.environ aquí, usamos la variable MI_API_KEY cargada arriba
    if not MI_API_KEY: 
        return "⚠️ Error: No se encontró la OPENAI_API_KEY en el archivo .env"
    
    client = OpenAI(api_key=MI_API_KEY)
    
    system_prompt = f"""
    Eres GIA, la asistente virtual de GeoInnova.
    Responde basándote en este documento:
    {CONOCIMIENTO_BASE}
    """
    
    messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.messages[-4:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": prompt})

    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0.2)
        return resp.choices[0].message.content
    except Exception as e: return f"Error: {e}"

# ---------- INTERFAZ DE CHAT ----------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Hola! Soy **GIA**. ¿En qué puedo ayudarte hoy?"}
    ]

assistant_avatar = str(AVATAR_PATH) if AVATAR_PATH.exists() else "🤖"
user_avatar = str(USER_AVATAR_PATH) if USER_AVATAR_PATH.exists() else "👤"

for msg in st.session_state.messages:
    avatar_icon = assistant_avatar if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.markdown(msg["content"])

if prompt := st.chat_input("Escribe tu pregunta..."):
    # Guardar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Mostrar mensaje del usuario inmediatamente con su nuevo avatar verde agua
    with st.chat_message("user", avatar=user_avatar):
        st.markdown(prompt)

    # Respuesta del asistente
    with st.chat_message("assistant", avatar=assistant_avatar):
        with st.spinner("GIA está pensando..."):
            respuesta = answer_query(prompt)
            st.markdown(respuesta)
            
    st.session_state.messages.append({"role": "assistant", "content": respuesta})