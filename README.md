## Requisitos de Instalaciónasdasd

Este proyecto está optimizado para funcionar con **Python 3.11** (Streamlit garantiza estabilidad hasta la versión 3.12). 

Para preparar tu entorno, abre una terminal en la carpeta del proyecto y ejecuta los siguientes comandos:

```bash
# 1. Actualizar el gestor de paquetes
py -3.11 -m pip install --upgrade pip

# 2. Instalar librerías de interfaz y mapas
py -3.11 -m pip install streamlit streamlit-folium folium

# 3. Instalar dependencias de IA y utilidades
py -3.11 -m pip install openai pandas python-dotenv

## Cómo ejecutar la aplicación

Cada vez que desees iniciar el chatbot, abre la terminal en la carpeta del proyecto y ejecuta:
```bash
py -3.11 -m streamlit run app.py

