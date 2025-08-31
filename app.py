import streamlit as st
import spacy
import csv
import io
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="🔍 Subjuntivo Finder",
    page_icon="🔍",
    layout="wide"
)

# Cargar el modelo de spaCy
@st.cache_resource
def load_nlp():
    return spacy.load("es_core_news_sm")

nlp = load_nlp()

# Título y descripción
st.title("🔍 Buscador de Verbos en Modo Subjuntivo")
st.markdown("""
Sube un archivo de texto en español y esta app identificará todos los verbos conjugados en **modo subjuntivo**.
Incluye resaltado en el texto, estadísticas y descarga en CSV.
""")

# Subida de archivo
uploaded_file = st.file_uploader("📤 Sube tu archivo .txt", type=["txt"])

if uploaded_file is not None:
    try:
        # Leer el archivo
        text = uploaded_file.read().decode("utf-8")
        st.success("✅ Archivo cargado correctamente.")

        # Procesar el texto
        doc = nlp(text)

        # Extraer verbos en subjuntivo
        with st.spinner("Analizando verbos en subjuntivo..."):
            subjunctive_verbs = []
            for token in doc:
                if token.pos_ == "VERB":
                    mood = token.morph.get("Mood")
                    if "Sub" in mood:
                        subjunctive_verbs.append({
                            "Verbo": token.text,
                            "Lema": token.lemma_,
                            "Modo": "Subjuntivo",
                            "Tiempo": token.morph.get("Tense", [""])[0] or "Desconocido",
                            "Persona": token.morph.get("Person", [""])[0] or "Desconocido",
                            "Número": token.morph.get("Number", [""])[0] or "Desconocido",
                            "Origen": token.sent.text.strip()  # oración completa
                        })

        # Mostrar resultados
        if subjunctive_verbs:
            df = pd.DataFrame(subjunctive_verbs)
            total = len(df)

            st.subheader(f"🎉 Se encontraron {total} verbos en subjuntivo")

            # Pestañas para organizar
            tab1, tab2, tab3 = st.tabs(["📊 Estadísticas", "📄 Texto con resaltado", "📋 Tabla completa"])

            # --- PESTAÑA 1: Gráficos ---
            with tab1:
                col1, col2, col3 = st.columns(3)

                with col1:
                    fig1 = px.pie(df, names="Tiempo", title="📌 Por tiempo verbal")
                    st.plotly_chart(fig1, use_container_width=True)

                with col2:
                    fig2 = px.pie(df, names="Persona", title="👤 Por persona")
                    st.plotly_chart(fig2, use_container_width=True)

                with col3:
                    fig3 = px.pie(df, names="Número", title="🔢 Por número")
                    st.plotly_chart(fig3, use_container_width=True)

                # Tabla de frecuencias
                st.markdown("### 🔤 Frecuencia por forma verbal")
                freq = df["Verbo"].value_counts().reset_index()
                freq.columns = ["Verbo", "Frecuencia"]
                st.dataframe(freq, use_container_width=True)

            # --- PESTAÑA 2: Texto con resaltado ---
            with tab2:
                st.markdown("### 📝 Texto original con verbos en subjuntivo resaltados")

                # Resaltar verbos en HTML
                highlighted_text = text
                for verb in sorted(set(df["Verbo"]), key=len, reverse=True):  # orden por longitud
                    highlight = f'<mark style="background-color: #FFEB3B; border-radius: 3px; padding: 2px 4px; margin: 0 2px;">{verb}</mark>'
                    # Usamos expresión regular para evitar resaltar partes de palabras
                    highlighted_text = re.sub(rf'\b({re.escape(verb)})\b', highlight, highlighted_text)

                st.markdown(
                    f'<div style="line-height: 1.8; font-size: 16px; padding: 15px; background-color: #f9f9f9; border-radius: 8px;">{highlighted_text}</div>',
                    unsafe_allow_html=True
                )

            # --- PESTAÑA 3: Tabla completa ---
            with tab3:
                st.dataframe(df, use_container_width=True)

            # --- Descarga CSV ---
            def convert_to_csv(dataframe):
                return dataframe.to_csv(index=False).encode("utf-8")

            csv_data = convert_to_csv(df)
            filename = f"subjuntivo_{uploaded_file.name.replace('.txt', '')}.csv"

            st.download_button(
                label="⬇️ Descargar resultados como CSV",
                data=csv_data,
                file_name=filename,
                mime="text/csv"
            )

        else:
            st.info("ℹ️ No se encontraron verbos en modo subjuntivo en el texto.")

    except Exception as e:
        st.error(f"❌ Ocurrió un error al procesar el archivo: {e}")
else:
    st.info("👈 Por favor, sube un archivo de texto (.txt) para comenzar.")

# Barra lateral
with st.sidebar:
    st.header("ℹ️ Acerca de")
    st.markdown("""
    Esta app analiza textos en español y detecta automáticamente verbos en **modo subjuntivo** usando procesamiento del lenguaje natural.

    ### Funcionalidades:
    - ✅ Resaltado de verbos en el texto
    - 📊 Gráficos por tiempo, persona y número
    - 📥 Descarga en CSV
    - 🧠 Basado en `spaCy` + `es_core_news_sm`

    Ideal para:
    - Estudiantes de ELE
    - Profesores de gramática
    - Investigación lingüística
    """)

# Para usar expresiones regulares
import re
