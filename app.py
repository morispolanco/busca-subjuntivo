import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Configuración de la página
st.set_page_config(page_title="🔍 Subjuntivo Finder", layout="wide")
st.title("🔍 Buscador de Verbos en Modo Subjuntivo")
st.markdown("""
Sube un archivo de texto en español y esta app identificará todos los verbos conjugados en **modo subjuntivo**.
Basado en reglas gramaticales y formas verbales comunes.
""")

# === LISTA COMPLETA DE FORMAS VERBALES EN SUBJUNTIVO (comunes en español) ===
SUBJUNTIVO_DATABASE = {
    # === Presente de Subjuntivo ===
    # AR
    "hable": "hablar", "hables": "hablar", "hable": "hablar", "hablemos": "hablar", "habléis": "hablar", "hablen": "hablar",
    # ER
    "coma": "comer", "comas": "comer", "coma": "comer", "comamos": "comer", "comáis": "comer", "coman": "comer",
    # IR
    "vaya": "ir", "vayas": "ir", "vaya": "ir", "vayamos": "ir", "vayáis": "ir", "vayan": "ir",
    # SER
    "sea": "ser", "seas": "ser", "sea": "ser", "seamos": "ser", "seáis": "ser", "sean": "ser",
    # ESTAR
    "esté": "estar", "estés": "estar", "esté": "estar", "estemos": "estar", "estéis": "estar", "estén": "estar",
    # DAR
    "dé": "dar", "des": "dar", "dé": "dar", "demos": "dar", "deis": "dar", "den": "dar",
    # PODER
    "pueda": "poder", "puedas": "poder", "pueda": "poder", "podamos": "poder", "podáis": "poder", "puedan": "poder",
    # QUERER
    "quiera": "querer", "quieras": "querer", "quiera": "querer", "queramos": "querer", "queráis": "querer", "quieran": "querer",
    # SENTIR
    "sienta": "sentir", "sientas": "sentir", "sienta": "sentir", "sintamos": "sentir", "sintáis": "sentir", "sientan": "sentir",
    # VALER
    "valga": "valer", "valgas": "valer", "valga": "valer", "valgamos": "valer", "valgáis": "valer", "valgan": "valer",
    # CABER
    "quepa": "caber", "quepas": "caber", "quepa": "caber", "quepamos": "caber", "quepáis": "caber", "quepan": "caber",
    # HABER
    "haya": "haber", "hayas": "haber", "haya": "haber", "hayamos": "haber", "hayáis": "haber", "hayan": "haber",
    # VENIR
    "venga": "venir", "vengas": "venir", "venga": "venir", "vengamos": "venir", "vengáis": "venir", "vengan": "venir",
    # CONVENIR
    "convenza": "convencer", "convenzas": "convencer", "convenza": "convencer", "convenzamos": "convencer", "convenzáis": "convencer", "convenzan": "convencer",

    # === Imperfecto de Subjuntivo (-ra) ===
    "hablara": "hablar", "hablaras": "hablar", "hablara": "hablar", "habláramos": "hablar", "hablarais": "hablar", "hablaran": "hablar",
    "comiera": "comer", "comieras": "comer", "comiera": "comer", "comiéramos": "comer", "comierais": "comer", "comieran": "comer",
    "viviera": "vivir", "vivieras": "vivir", "viviera": "vivir", "viviéramos": "vivir", "vivierais": "vivir", "vivieran": "vivir",
    "fuera": "ser", "fueras": "ser", "fuera": "ser", "fuéramos": "ser", "fuerais": "ser", "fueran": "ser",
    "estuviera": "estar", "estuvieras": "estar", "estuviera": "estar", "estuviéramos": "estar", "estuvierais": "estar", "estuvieran": "estar",

    # === Imperfecto de Subjuntivo (-se) ===
    "hablase": "hablar", "hablases": "hablar", "hablase": "hablar", "hablásemos": "hablar", "hablaseis": "hablar", "hablasen": "hablar",
    "comiese": "comer", "comieses": "comer", "comiese": "comer", "comiésemos": "comer", "comieseis": "comer", "comiesen": "comer",
    "viviese": "vivir", "vivieses": "vivir", "viviese": "vivir", "viviésemos": "vivir", "vivieseis": "vivir", "viviesen": "vivir",
    "fuese": "ser", "fueses": "ser", "fuese": "ser", "fuésemos": "ser", "fueseis": "ser", "fuesen": "ser",
    "estuviese": "estar", "estuvieses": "estar", "estuviese": "estar", "estuviésemos": "estar", "estuvieseis": "estar", "estuviesen": "estar",

    # === Futuro de Subjuntivo (raro, pero por completitud) ===
    "hablare": "hablar", "hablares": "hablar", "hablare": "hablar", "habláremos": "hablar", "hablareis": "hablar", "hablaren": "hablar",
}

# Conjunto para búsquedas rápidas
SUBJ_VERBS = set(SUBJUNTIVO_DATABASE.keys())

def detect_subjunctive_words(text):
    words = re.findall(r'\b\w+\b', text, re.IGNORECASE)
    found = []
    seen = set()
    for word in words:
        lower_word = word.lower()
        if lower_word in SUBJ_VERBS and lower_word not in seen:
            # Determinar tiempo
            if re.search(r'(ra|se)mos|ramos|semos|rais|seis|ran|sen$', lower_word):
                tiempo = "Imperfecto"
            elif re.search(r're$', lower_word):
                tiempo = "Futuro"
            else:
                tiempo = "Presente"
            # Determinar número
            numero = "Plural" if lower_word.endswith(("mos", "is", "n", "áis", "ais")) else "Singular"
            # Determinar persona (aproximado)
            persona = "Desconocida"

            found.append({
                "Verbo": word,
                "Lema": SUBJUNTIVO_DATABASE[lower_word],
                "Tiempo": tiempo,
                "Modo": "Subjuntivo",
                "Persona": persona,
                "Número": numero
            })
            seen.add(lower_word)
    return found

# --- Interfaz ---
uploaded_file = st.file_uploader("📤 Sube tu archivo .txt", type=["txt"])

if uploaded_file is not None:
    try:
        text = uploaded_file.read().decode("utf-8")
        st.success("✅ Archivo cargado correctamente.")

        with st.expander("📄 Ver texto"):
            st.text(text)

        # Analizar
        verbs = detect_subjunctive_words(text)

        if verbs:
            df = pd.DataFrame(verbs)
            st.subheader(f"🎉 Se encontraron {len(df)} verbos en subjuntivo")

            tab1, tab2, tab3 = st.tabs(["📊 Estadísticas", "📄 Texto resaltado", "📋 Tabla completa"])

            with tab1:
                fig = px.pie(df, names="Tiempo", title="Distribución por tiempo verbal")
                st.plotly_chart(fig)

            with tab2:
                highlighted = text
                for verb in sorted(df["Verbo"].unique(), key=len, reverse=True):
                    highlighted = re.sub(
                        rf'\b({re.escape(verb)})\b',
                        f'<mark style="background: #FFEB3B; padding: 2px 6px; border-radius: 4px; font-weight: bold;">\\1</mark>',
                        highlighted,
                        flags=re.IGNORECASE
                    )
                st.markdown(
                    f'<div style="line-height: 1.8; padding: 15px; background: #f8f9fa; border-radius: 8px; font-size: 16px;">{highlighted}</div>',
                    unsafe_allow_html=True
                )

            with tab3:
                st.dataframe(df, use_container_width=True)

            # Descarga CSV
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Descargar como CSV",
                data=csv_data,
                file_name="verbos_subjuntivo.csv",
                mime="text/csv"
            )

        else:
            st.info("ℹ️ No se encontraron verbos en modo subjuntivo.")

    except Exception as e:
        st.error("❌ Error al procesar el archivo.")
        st.exception(e)
else:
    st.info("👈 Sube un archivo .txt para comenzar.")
