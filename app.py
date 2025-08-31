import streamlit as st
import spacy
import pandas as pd
import plotly.express as px
import re
import subprocess
import sys

# Configuración de página
st.set_page_config(page_title="🔍 Subjuntivo Finder", layout="wide")
st.title("🔍 Buscador de Verbos en Modo Subjuntivo")
st.markdown("Sube un archivo de texto en español para analizar verbos en **subjuntivo**.")

# --- FUNCIÓN MEJORADA PARA CARGAR EL MODELO ---
@st.cache_resource
def load_nlp():
    try:
        return spacy.load("es_core_news_sm")
    except OSError:
        st.error("❌ No se encontró el modelo 'es_core_news_sm'. Intentando instalarlo...")
        
        try:
            # Intentar instalar directamente desde la URL del modelo
            command = [
                sys.executable, "-m", "pip", "install",
                "https://github.com/explosion/spacy-models/releases/download/es_core_news_sm-3.7.0/es_core_news_sm-3.7.0.tar.gz"
            ]
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode != 0:
                st.error("❌ Falló la instalación del modelo.")
                st.code(result.stderr)
                st.stop()
            else:
                st.success("✅ Modelo instalado correctamente.")
                return spacy.load("es_core_news_sm")
        except Exception as e:
            st.error("❌ Error al instalar el modelo.")
            st.exception(e)
            st.stop()

# Cargar modelo
nlp = load_nlp()

# --- SUBIR Y ANALIZAR ARCHIVO ---
uploaded_file = st.file_uploader("📤 Sube tu archivo .txt", type=["txt"])

if uploaded_file is not None:
    try:
        text = uploaded_file.read().decode("utf-8")
        st.success("✅ Archivo cargado.")

        # Procesar con spaCy
        doc = nlp(text)
        verbs = []

        for token in doc:
            if token.pos_ == "VERB":
                mood = token.morph.get("Mood")
                if "Sub" in mood:
                    verbs.append({
                        "Verbo": token.text,
                        "Lema": token.lemma_,
                        "Modo": "Subjuntivo",
                        "Tiempo": token.morph.get("Tense", [""])[0] or "Desconocido",
                        "Persona": token.morph.get("Person", [""])[0] or "Desconocido",
                        "Número": token.morph.get("Number", [""])[0] or "Desconocido",
                        "Oración": token.sent.text.strip()
                    })

        if verbs:
            df = pd.DataFrame(verbs)
            st.subheader(f"🎉 Se encontraron {len(df)} verbos en subjuntivo")

            tab1, tab2, tab3 = st.tabs(["📊 Estadísticas", "📄 Texto resaltado", "📋 Detalles"])

            with tab1:
                col1, col2, col3 = st.columns(3)
                with col1:
                    fig = px.pie(df, names="Tiempo", title="Tiempo verbal")
                    st.plotly_chart(fig)
                with col2:
                    fig = px.pie(df, names="Persona", title="Persona")
                    st.plotly_chart(fig)
                with col3:
                    fig = px.pie(df, names="Número", title="Número")
                    st.plotly_chart(fig)

            with tab2:
                highlighted = text
                for verb in sorted(df["Verbo"].unique(), key=len, reverse=True):
                    highlighted = re.sub(
                        rf'\b({re.escape(verb)})\b',
                        f'<mark style="background: #FFEB3B; padding: 2px 6px; border-radius: 4px;">\\1</mark>',
                        highlighted
                    )
                st.markdown(
                    f'<div style="line-height: 1.8; padding: 15px; background: #f0f0f0; border-radius: 8px; max-height: 400px; overflow-y: auto;">{highlighted}</div>',
                    unsafe_allow_html=True
                )

            with tab3:
                st.dataframe(df, use_container_width=True)

            # Descarga CSV
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Descargar CSV",
                data=csv_data,
                file_name=f"subjuntivo_{uploaded_file.name.replace('.txt', '')}.csv",
                mime="text/csv"
            )

        else:
            st.info("ℹ️ No se encontraron verbos en subjuntivo.")

    except Exception as e:
        st.error("❌ Error al procesar el texto.")
        st.exception(e)
else:
    st.info("👈 Sube un archivo .txt para comenzar.")

# Barra lateral
with st.sidebar:
    st.header("ℹ️ Acerca de")
    st.markdown("""
    Esta app detecta verbos en **modo subjuntivo** en textos en español.
    
    ### ¿Qué detecta?
    - hable, hables, hablemos
    - fuera, fuerais, estés, pueda, vayas, etc.
    
    Ideal para estudiantes y profesores de ELE.
    """)
