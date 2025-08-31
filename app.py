import streamlit as st
import spacy
import csv
import io
import pandas as pd
import plotly.express as px
import re

# Configuración de la página
st.set_page_config(
    page_title="🔍 Subjuntivo Finder",
    page_icon="🔍",
    layout="wide"
)

# Cargar el modelo de spaCy (una sola vez, en caché)
@st.cache_resource
def load_nlp():
    try:
        return spacy.load("es_core_news_sm")
    except OSError as e:
        st.error(f"""
        ❌ No se pudo cargar el modelo 'es_core_news_sm'.  
        Asegúrate de que está en `requirements.txt` como:
        
        `https://github.com/explosion/spacy-models/releases/download/es_core_news_sm-3.7.0/es_core_news_sm-3.7.0.tar.gz`
        
        Error: {e}
        """)
        st.stop()

nlp = load_nlp()

# Título
st.title("🔍 Buscador de Verbos en Modo Subjuntivo")
st.markdown("Sube un archivo de texto en español para analizar verbos en **subjuntivo**.")

# Subida de archivo
uploaded_file = st.file_uploader("📤 Sube tu archivo .txt", type=["txt"])

if uploaded_file is not None:
    try:
        text = uploaded_file.read().decode("utf-8")
        st.success("✅ Archivo cargado.")

        # Análisis
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
            st.subheader(f"🎉 {len(df)} verbos en subjuntivo encontrados")

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
        st.error(f"❌ Error al procesar el archivo: {e}")
else:
    st.info("👈 Sube un archivo .txt para comenzar.")

# Barra lateral
with st.sidebar:
    st.header("ℹ️ Ayuda")
    st.markdown("""
    - Solo archivos `.txt` en español.
    - El modelo reconoce formas como: *hable, estés, fuera, vayamos*.
    - Usa `requirements.txt` con el modelo descargable.
    """)
