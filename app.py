import os
import base64
from pathlib import Path
import streamlit as st
from PyPDF2 import PdfReader
from openai import OpenAI

# ---------- 🔑 CONFIGURACIÓN API KEY 🔑 ----------
MI_API_KEY = "TU-API-KEY-AQUI" 
os.environ["OPENAI_API_KEY"] = MI_API_KEY
# ------------------------------------------------

# ---------- DEFINICIÓN DE RUTAS ----------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
PDF_PATH = DATA_DIR / "Política y Procedimiento Personas - Beneficios. 2025.pdf"

# 1. IMAGEN PARA EL TÍTULO (Logo GeoInnova - Rectángulo Rojo)
LOGO_PATH = ASSETS_DIR / "0.png" 

# 2. IMAGEN PARA EL CHAT (Avatar de GIA - Rectángulo Azul)
# NOTA: Asegúrate de que este archivo exista en la carpeta assets.
# Te recomiendo renombrar tu archivo largo a "gia_avatar.png"
AVATAR_FILENAME = "ABS2GSmt7b7Sr4iYhuLYWh6E1OusDIWhbmTr__1WlmLtyh2cynvh8C_7OhaIzsj5PPSVpVkEbJKP2eY9vsz49aYtmQYH4oM23l7JSyyt0dB2y2iU3wZ4gJYYjduUMoQgpNCG3GpM68AdEkviTEpxiKkbG5fIqmxeOUu6k0GBusFLtq4x0LyGs1024-rj.png"
# Si prefieres usar el nombre original largo, cambia la línea de arriba por:
# AVATAR_FILENAME = "ChatGPT Image 10 dic 2025, 04_42_04 p.m..png"

AVATAR_PATH = ASSETS_DIR / AVATAR_FILENAME

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

# ---------- LÓGICA DE DATOS Y IA ----------
@st.cache_data
def cargar_conocimiento_pdf(filepath):
    if not filepath.exists(): return None
    try:
        reader = PdfReader(str(filepath))
        text = ""
        for page in reader.pages: text += page.extract_text() + "\n"
        return text
    except Exception as e: return f"Error PDF: {e}"

CONOCIMIENTO_BASE = cargar_conocimiento_pdf(PDF_PATH)

if not CONOCIMIENTO_BASE:
    st.error(f"⚠️ No se encontró el documento: {PDF_PATH}")
    st.stop()

def answer_query(prompt: str):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key: return "⚠️ Falta API Key."
    
    client = OpenAI(api_key=api_key)
    system_prompt = f"""
    Eres GIA, asistente virtual de GeoInnova.
    Responde dudas basándote en el siguiente texto.
    Si no sabes la respuesta, indícalo.
    
    DOCUMENTO:
    {CONOCIMIENTO_BASE[:50000]}
    """
    messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.messages[-4:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": prompt})

    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0.0)
        return resp.choices[0].message.content
    except Exception as e: return f"Error: {e}"

# ---------- INTERFAZ DE CHAT (CON AVATAR PERSONALIZADO) ----------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Hola! Soy **GIA**. ¿En qué puedo ayudarte hoy?"}
    ]

# Definimos cuál imagen usar para el avatar del asistente
# Aquí usamos AVATAR_PATH (la nueva imagen que subiste)
assistant_avatar = str(AVATAR_PATH) if AVATAR_PATH.exists() else "🤖"

for msg in st.session_state.messages:
    # Si el mensaje es del asistente, usamos tu imagen nueva. Si es usuario, dejamos None (default)
    avatar_icon = assistant_avatar if msg["role"] == "assistant" else None
    
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.markdown(msg["content"])

if prompt := st.chat_input("Escribe tu pregunta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=assistant_avatar):
        with st.spinner("GIA está pensando..."):
            respuesta = answer_query(prompt)
            st.markdown(respuesta)
            
    st.session_state.messages.append({"role": "assistant", "content": respuesta})