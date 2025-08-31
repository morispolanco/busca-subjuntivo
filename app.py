import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Configuración
st.set_page_config(page_title="🔍 Subjuntivo Finder", layout="wide")
st.title("🔍 Buscador de Verbos en Subjuntivo")
st.markdown("""
Detecta automáticamente verbos en **modo subjuntivo** mediante reglas gramaticales y lista de formas comunes.
Funciona 100% sin internet ni tokens.
""")

# === BASE DE FORMAS VERBALES EN SUBJUNTIVO (comunes) ===
SUBJUNTIVO_FORMS = {
    # Presente
    "hable": "hablar", "hables": "hablar", "hable": "hablar", "hablemos": "hablar", "habléis": "hablar", "hablen": "hablar",
    "coma": "comer", "comas": "comer", "coma": "comer", "comamos": "comer", "comáis": "comer", "coman": "comer",
    "vaya": "ir", "vayas": "ir", "vaya": "ir", "vayamos": "ir", "vayáis": "ir", "vayan": "ir",
    "sea": "ser", "seas": "ser", "sea": "ser", "seamos": "ser", "seáis": "ser", "sean": "ser",
    "esté": "estar", "estés": "estar", "esté": "estar", "estemos": "estar", "estéis": "estar", "estén": "estar",
    "dé": "dar", "des": "dar", "dé": "dar", "demos": "dar", "deis": "dar", "den": "dar",
    "pueda": "poder", "puedas": "poder", "pueda": "poder", "podamos": "poder", "podáis": "poder", "puedan": "poder",
    "quiera": "querer", "quieras": "querer", "quiera": "querer", "queramos": "querer", "queráis": "querer", "quieran": "querer",
    "sienta": "sentir", "sientas": "sentir", "sienta": "sentir", "sintamos": "sentir", "sintáis": "sentir", "sientan": "sentir",
    "valga": "valer", "valgas": "valer", "valga": "valer", "valgamos": "valer", "valgáis": "valer", "valgan": "valer",
    "cabe": "caber", "quepa": "caber", "quepan": "caber", "convenga": "convenir", "convengan": "convenir",
    "haya": "haber", "hayas": "haber", "haya": "haber", "hayamos": "haber", "hayáis": "haber", "hayan": "haber",
    "venga": "venir", "vengas": "venir", "venga": "venir", "vengamos": "venir", "vengáis": "venir", "vengan": "venir",

    # Imperfecto (-ra)
    "hablara": "hablar", "hablaras": "hablar", "hablara": "hablar", "habláramos": "hablar", "hablarais": "hablar", "hablaran": "hablar",
    "comiera": "comer", "comieras": "comer", "comiera": "comer", "comiéramos": "comer", "comierais": "comer", "comieran": "comer",
    "fuera": "ser", "fueras": "ser", "fuera": "ser", "fuéramos": "ser", "fuerais": "ser", "fueran": "ser",
    "estuviera": "estar", "estuvieras": "estar", "estuviera": "estar", "estuviéramos": "estar", "estuvierais": "estar", "estuvieran": "estar",

    # Imperfecto (-se)
    "hablase": "hablar", "hablases": "hablar", "hablase": "hablar", "hablásemos": "hablar", "hablaseis": "hablar", "hablasen": "hablar",
    "comiese": "comer", "comieses": "comer", "comiese": "comer", "comiésemos": "comer", "comieseis": "comer", "comiesen": "comer",
    "fuese": "ser", "fueses": "ser", "fuese": "ser", "fuésemos": "ser", "fueseis": "ser", "fuesen": "ser",

    # Futuro (raro)
    "hablare": "hablar", "hablares": "hablar", "hablare": "hablar", "habláremos": "hablar", "hablareis": "hablar", "hablaren": "hablar",
}

# Convertir a conjunto para búsquedas rápidas
SUBJ_SET = set(SUBJUNTIVO_FORMS.keys())

# Función para detectar verbos
def find_subjunctive(text):
    words = re.findall(r'\b\w+\b', text, re.IGNORECASE)
    verbs = []
    seen = set()
    for word in words:
        w = word.lower()
        if w in SUBJ_SET and w not in seen:
            verbs.append({
                "Verbo": word,
                "Lema": SUBJUNTIVO_FORMS[w],
                "Modo": "Subjuntivo",
                "Tiempo": "Presente" if re.search(r'(e|a|emos|áis|an|as|es)$', w) else
                         "Imperfecto" if re.search(r'(ra|se|ramos|semos|rais|seis|ran|sen)$', w) else
                         "Futuro",
                "Persona": "Desconocida",
                "Número": "Singular" if w.endswith(("a", "e", "o", "ra", "se")) and not w.endswith(("amos", "áis", "emos", "seis")) else "Plural"
            })
            seen.add(w)
    return verbs

# --- Interfaz ---
uploaded_file = st.file_uploader("📤 Sube tu archivo .txt", type=["txt"])

if uploaded_file is not None:
    try:
        text = uploaded_file.read().decode("utf-8")
        st.success("✅ Archivo cargado.")

        verbs = find_subjunctive(text)
        if verbs:
            df = pd.DataFrame(verbs)
            st.subheader(f"🎉 Se encontraron {len(df)} verbos en subjuntivo")

            tab1, tab2, tab3 = st.tabs(["📊 Estadísticas", "📄 Texto resaltado", "📋 Detalles"])

            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    fig1 = px.pie(df, names="Tiempo", title="Tiempo verbal")
                    st.plotly_chart(fig1)
                with col2:
                    fig2 = px.pie(df, names="Lema", title="Verbos más comunes")
                    st.plotly_chart(fig2)

            with tab2:
                highlighted = text
                for verb in sorted(df["Verbo"].unique(), key=len, reverse=True):
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

            with tab3:
                st.dataframe(df, use_container_width=True)

            # Descarga CSV
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Descargar CSV",
                data=csv_data,
                file_name="verbos_subjuntivo.csv",
                mime="text/csv"
            )
        else:
            st.info("ℹ️ No se encontraron verbos en subjuntivo.")

    except Exception as e:
        st.error("❌ Error al leer el archivo.")
        st.exception(e)
else:
    st.info("👈 Sube un archivo .txt para comenzar.")
