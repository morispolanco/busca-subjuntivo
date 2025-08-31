import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import re

# Configuración
st.set_page_config(page_title="🔍 Subjuntivo Finder con LLM", layout="wide")
st.title("🔍 Buscador de Verbos en Subjuntivo con IA")
st.markdown("Usa un modelo de inteligencia artificial para detectar verbos en modo subjuntivo en español.")

# --- Modelo público que no requiere acceso especial ---
API_URL = "https://api-inference.huggingface.co/models/mrm8488/bert-small2bert-small-finetuned-squadv2-es"
# Nota: Este modelo no requiere token para inferencia básica, pero va más rápido con uno

HEADERS = {}  # Sin token obligatorio

def query_llm(text):
    # Vamos a usar el modelo como generador de respuestas
    prompt = f"""
    Extrae todos los verbos en modo subjuntivo del siguiente texto en español.
    Indica: forma verbal, lema, tiempo, persona, número.
    Texto: {text[:500]}
    Formato: JSON con lista de objetos.
    """
    payload = {
        "inputs": {
            "question": prompt,
            "context": text[:1000]
        }
    }

    try:
        response = requests.post(API_URL, json=payload, headers=HEADERS)
        if response.status_code == 200:
            output = response.json()
            answer = output.get("answer", "") or str(output)
            return parse_json_from_text(answer)
        elif response.status_code == 503:
            st.warning("⏳ El modelo está cargándose. Por favor, intenta de nuevo en 1-2 minutos.")
        else:
            st.error(f"❌ Error {response.status_code}: {response.text}")
            return []
    except Exception as e:
        st.error("❌ No se pudo conectar con Hugging Face.")
        st.exception(e)
        return []

def parse_json_from_text(text):
    import json
    try:
        start = text.find("[")
        end = text.rfind("]") + 1
        if start == -1 or end == 0:
            return []
        json_str = text[start:end]
        return json.loads(json_str)
    except:
        return []

# --- Interfaz ---
uploaded_file = st.file_uploader("📤 Sube tu archivo .txt", type=["txt"])

if uploaded_file is not None:
    try:
        text = uploaded_file.read().decode("utf-8")
        st.success("✅ Archivo cargado.")

        if st.button("🔍 Analizar con IA"):
            with st.spinner("🧠 Analizando con modelo de español..."):
                result = query_llm(text)

            if result:
                df = pd.DataFrame(result)
                if "verbo" in df.columns:
                    df["Modo"] = "Subjuntivo"
                    df = df[["verbo", "lema", "tiempo", "persona", "numero", "Modo"]]

                    st.subheader(f"🎉 {len(df)} verbos encontrados")
                    st.dataframe(df, use_container_width=True)

                    col1, col2 = st.columns(2)
                    with col1:
                        if "tiempo" in df.columns:
                            fig = px.pie(df, names="tiempo", title="Tiempo verbal")
                            st.plotly_chart(fig)
                    with col2:
                        if "persona" in df.columns:
                            fig = px.pie(df, names="persona", title="Persona")
                            st.plotly_chart(fig)

                    # Resaltado
                    highlighted = text
                    for verb in sorted(df["verbo"].unique(), key=len, reverse=True):
                        highlighted = re.sub(
                            rf'\b({re.escape(verb)})\b',
                            f'<mark style="background: #FFEB3B; padding: 2px 6px; border-radius: 4px;">\\1</mark>',
                            highlighted,
                            flags=re.IGNORECASE
                        )
                    st.markdown(
                        f'<div style="line-height: 1.8; padding: 15px; background: #f0f0f0; border-radius: 8px;">{highlighted}</div>',
                        unsafe_allow_html=True
                    )

                    # Descarga
                    csv_data = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "⬇️ Descargar CSV",
                        data=csv_data,
                        file_name="subjuntivo.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("ℹ️ No se extrajeron campos estructurados.")
            else:
                st.info("ℹ️ No se encontraron verbos o el modelo no respondió.")
    except Exception as e:
        st.error("❌ Error al procesar el archivo.")
        st.exception(e)
else:
    st.info("👈 Sube un archivo .txt para comenzar.")
