import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import re

# Configuración de la página
st.set_page_config(page_title="🔍 Subjuntivo Finder con LLM", layout="wide")
st.title("🔍 Buscador de Verbos en Subjuntivo con LLM")
st.markdown("""
Esta app usa un **modelo de inteligencia artificial** para detectar verbos en modo subjuntivo en español.
Analiza tu texto y muestra resultados con tabla, gráficos y texto resaltado.
""")
st.info("🔐 El token de Hugging Face se carga de forma segura. Asegúrate de configurarlo en 'Secrets'.")

# --- Configuración del modelo Hugging Face ---
API_URL = "https://api-inference.huggingface.co/models/PlanTL-GOB-ES/roberta-base-bne"

def query_llm(text, token):
    headers = {"Authorization": f"Bearer {token}"}
    prompt = f"""
Analiza el siguiente texto en español y extrae todos los verbos en modo subjuntivo.
Para cada verbo, indica:
- Forma verbal (ej: hables)
- Lema (infinitivo, ej: hablar)
- Tiempo (presente, imperfecto)
- Persona (1ª, 2ª, 3ª)
- Número (singular, plural)

Texto: {text[:1000]}  # Limitar tamaño

Responde en formato JSON válido:
[{{"verbo": "...", "lema": "...", "tiempo": "...", "persona": "...", "numero": "..."}}]
""".strip()

    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        if response.status_code == 200:
            output = response.json()
            text_out = output[0]["generated_text"] if isinstance(output, list) and len(output) > 0 else str(output)
            return parse_json_from_text(text_out)
        else:
            st.error(f"❌ Error {response.status_code}: {response.text}")
            return []
    except Exception as e:
        st.error("❌ No se pudo conectar con Hugging Face. Revisa tu token o el modelo.")
        st.exception(e)
        return []

def parse_json_from_text(text):
    import json
    try:
        start = text.find("[")
        end = text.rfind("]") + 1
        if start == -1 or end == 0:
            st.warning("⚠️ No se encontró JSON en la respuesta. Mostrando texto crudo.")
            st.text(text[:500])
            return []
        json_str = text[start:end]
        return json.loads(json_str)
    except Exception as e:
        st.error("❌ No se pudo parsear la respuesta del modelo.")
        st.text(text[:300])
        return []

# --- Carga del token desde secrets (seguro) ---
try:
    HF_TOKEN = st.secrets["HF_TOKEN"]
except Exception as e:
    st.error("🔐 No se encontró el token de Hugging Face.")
    st.markdown("""
    ### Configura tu token:
    1. Ve a [Hugging Face Tokens](https://huggingface.co/settings/tokens) y crea uno nuevo (rol: `Inference API`).
    2. En Streamlit Cloud, ve a tu app → **"Settings" → "Secrets"**.
    3. Pega:
    ```toml
    HF_TOKEN = "hf_tuTokenAqui"
    ```
    4. Guarda y reinicia.
    """)
    st.stop()

# --- Interfaz principal ---
uploaded_file = st.file_uploader("📤 Sube tu archivo .txt", type=["txt"])

if uploaded_file is not None:
    try:
        text = uploaded_file.read().decode("utf-8")
        st.success("✅ Archivo cargado.")
        
        with st.expander("📄 Ver texto cargado"):
            st.text(text[:1000] + ("..." if len(text) > 1000 else ""))

        if st.button("🔍 Analizar con IA (LLM)"):
            with st.spinner("🧠 El modelo está analizando el texto... (puede tardar 10-20 seg)"):
                result = query_llm(text, HF_TOKEN)

            if result:
                df = pd.DataFrame(result)
                df["Modo"] = "Subjuntivo"
                df = df[["verbo", "lema", "tiempo", "persona", "numero", "Modo"]]

                st.subheader(f"🎉 Se encontraron {len(df)} verbos en subjuntivo")

                tab1, tab2 = st.tabs(["📊 Resultados", "📄 Texto resaltado"])

                with tab1:
                    st.dataframe(df, use_container_width=True)

                    # Gráficos si hay datos
                    col1, col2 = st.columns(2)
                    with col1:
                        if "tiempo" in df.columns:
                            fig1 = px.pie(df, names="tiempo", title="Tiempo verbal")
                            st.plotly_chart(fig1)
                    with col2:
                        if "persona" in df.columns:
                            fig2 = px.pie(df, names="persona", title="Persona")
                            st.plotly_chart(fig2)

                with tab2:
                    highlighted = text
                    for verb in sorted(df["verbo"].unique(), key=len, reverse=True):
                        highlighted = re.sub(
                            rf'\b({re.escape(verb)})\b',
                            f'<mark style="background: #FFEB3B; padding: 2px 6px; border-radius: 4px;">\\1</mark>',
                            highlighted,
                            flags=re.IGNORECASE
                        )
                    st.markdown(
                        f'<div style="line-height: 1.8; padding: 15px; background: #f0f0f0; border-radius: 8px; max-height: 400px; overflow-y: auto;">{highlighted}</div>',
                        unsafe_allow_html=True
                    )

                # Descarga CSV
                csv_data = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Descargar resultados como CSV",
                    data=csv_data,
                    file_name="verbos_subjuntivo.csv",
                    mime="text/csv"
                )
            else:
                st.info("ℹ️ No se encontraron verbos en subjuntivo o el modelo no respondió correctamente.")

    except Exception as e:
        st.error("❌ Error al leer el archivo.")
        st.exception(e)
else:
    st.info("👈 Sube un archivo .txt para comenzar.")
