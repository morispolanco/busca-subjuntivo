import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Configuración
st.set_page_config(page_title="🔍 Subjuntivo Finder (con contexto)", layout="wide")
st.title("🔍 Buscador de Verbos en Subjuntivo con Análisis Contextual")
st.markdown("""
Esta app detecta verbos en modo subjuntivo **evitando confundirlos con el imperativo**,
analizando **la forma verbal + su contexto gramatical**.
""")

# === BASE DE DATOS DE FORMAS VERBALES EN SUBJUNTIVO ===
SUBJUNTIVO_COMPLETO = {
    # (Incluye todas las formas del mensaje anterior, por brevedad no se repite aquí)
    # Pero en tu app, ponemos la lista completa (como la que ya tienes)
    # Aquí solo ponemos un subconjunto de ejemplo
    "hable": "hablar", "hables": "hablar", "hablemos": "hablar", "habléis": "hablar", "hablen": "hablar",
    "coma": "comer", "comas": "comer", "comamos": "comer", "comáis": "comer", "coman": "comer",
    "vaya": "ir", "vayas": "ir", "vayamos": "ir", "vayáis": "ir", "vayan": "ir",
    "sea": "ser", "seas": "ser", "seamos": "ser", "seáis": "ser", "sean": "ser",
    "esté": "estar", "estés": "estar", "estemos": "estar", "estéis": "estar", "estén": "estar",
    "dé": "dar", "des": "dar", "demos": "dar", "deis": "dar", "den": "dar",
    "pueda": "poder", "puedas": "poder", "podamos": "poder", "podáis": "poder", "puedan": "poder",
    "quiera": "querer", "quieras": "querer", "queramos": "querer", "queráis": "querer", "quieran": "querer",
    "sienta": "sentir", "sientas": "sentir", "sintamos": "sentir", "sintáis": "sentir", "sientan": "sentir",
    "valga": "valer", "valgas": "valer", "valgamos": "valer", "valgáis": "valer", "valgan": "valer",
    "haya": "haber", "hayas": "haber", "hayamos": "haber", "hayáis": "haber", "hayan": "haber",
    "venga": "venir", "vengas": "venir", "vengamos": "venir", "vengáis": "venir", "vengan": "venir",
    "fuera": "ser", "fueras": "ser", "fuéramos": "ser", "fuerais": "ser", "fueran": "ser",
    "estuviera": "estar", "estuvieras": "estar", "estuviéramos": "estar", "estuvierais": "estar", "estuvieran": "estar",
    "fuese": "ser", "fueses": "ser", "fuésemos": "ser", "fueseis": "ser", "fuesen": "ser",
    "estuviese": "estar", "estuvieses": "estar", "estuviésemos": "estar", "estuvieseis": "estar", "estuviesen": "estar",
    # ... (añade el resto de tu lista completa aquí)
}

SUBJ_SET = set(SUBJUNTIVO_COMPLETO.keys())

# === EXPRESIONES QUE INTRODUCEN SUBJUNTIVO (contexto) ===
TRIGGERS_SUBJUNTIVO = [
    r'\bque\b', r'\baunque\b', r'\baunque\b', r'\ba pesar de que\b', r'\bcomo si\b',
    r'\bantes de que\b', r'\bhasta que\b', r'\bdespués de que\b', r'\bpara que\b',
    r'\bporque\b', r'\ba fin de que\b', r'\bno creo que\b', r'\bdudo que\b',
    r'\bes importante que\b', r'\bes necesario que\b', r'\bes bueno que\b',
    r'\bme alegra que\b', r'\blo siento que\b', r'\bme sorprende que\b',
    r'\bojalá que?\b', r'\bquizá(s)? que?\b', r'\btal vez que?\b',
    r'\bsin que\b', r'\bsalvo que\b', r'\bexcepto que\b', r'\ba menos que\b',
    r'\bpara que\b', r'\ben caso de que\b', r'\bsiempre que\b', r'\bcuando\b',
    r'\bmientras que\b', r'\bpor más que\b', r'\bpor mucho que\b',
]

# === EXPRESIONES QUE INDICAN IMPERATIVO (contexto) ===
TRIGGERS_IMPERATIVO = [
    r'\busted\b', r'\bus\.t\.\b', r'\bu[ds]t[ed]d\b', r'\bvosotros?\b', r'\bvosotras?\b',
    r'\ba la orden\b', r'\bpor favor\b', r'\bporfa\b', r'\bporfi\b', r'\bordena\b',
    r'\bmandato\b', r'\bimperativo\b', r'\bordena\b',
]

# === Detectar contexto ===
def get_context(sentence, verb_start):
    before = sentence[:verb_start].strip()
    after = sentence[verb_start:].strip()
    return before, after

def is_imperative_context(before, after, verb):
    # Si hay "usted", "ustedes", "por favor", etc., es probablemente imperativo
    before_lower = before.lower()
    after_lower = after.lower()

    # Reglas de imperativo
    if re.search(r'\busted(es)?\b', before_lower + " " + after_lower):
        return True
    if re.search(r'\bpor favor\b', before_lower + " " + after_lower):
        return True
    if re.search(r'^[A-Z].*[,\.]?\s*$|^¡.*!$', before + " " + after):  # Frase imperativa clásica
        return True
    if re.search(r'\bordena\b|\bmandato\b', before_lower + after_lower):
        return True
    return False

def is_subjunctive_context(before, after):
    before_lower = before.lower()
    after_lower = after.lower()
    full = before_lower + " " + after_lower
    return any(re.search(trigger, full) for trigger in TRIGGERS_SUBJUNTIVO)

def detectar_subjuntivo(texto):
    # Dividimos en oraciones
    oraciones = re.split(r'[.!?]+', texto)
    encontrados = []
    vistos = set()

    for oracion cruda in oraciones:
        oracion = oracion.strip()
        if not oracion:
            continue

        palabras = re.findall(r'\b\w+\b', oracion)
        for palabra in palabras:
            forma = palabra.lower()
            if forma in SUBJ_SET and forma not in vistos:
                # Buscar posición de la palabra en la oración
                match = re.search(r'\b' + re.escape(palabra) + r'\b', oracion, re.IGNORECASE)
                if not match:
                    continue
                pos = match.start()

                before, after = get_context(oracion, pos)

                # Clasificar
                es_por_contexto_subj = is_subjunctive_context(before, after)
                es_por_contexto_imp = is_imperative_context(before, after, forma)

                if es_por_contexto_imp and not es_por_contexto_subj:
                    # Es imperativo, no subjuntivo
                    continue
                elif es_por_contexto_subj:
                    # Es subjuntivo por contexto
                    clasificacion = "Seguro"
                else:
                    # Ambiguo, pero forma coincide → "Posible"
                    clasificacion = "Posible (sin contexto claro)"

                # Determinar tiempo
                if forma.endswith(("ra", "se", "ramos", "semos", "rais", "seis", "ran", "sen")):
                    tiempo = "Imperfecto"
                elif forma.endswith("re"):
                    tiempo = "Futuro"
                else:
                    tiempo = "Presente"

                # Número
                numero = "Plural" if forma.endswith(("mos", "is", "n", "áis", "ais")) else "Singular"

                encontrados.append({
                    "Verbo": palabra,
                    "Lema": SUBJUNTIVO_COMPLETO[forma],
                    "Tiempo": tiempo,
                    "Modo": "Subjuntivo",
                    "Número": numero,
                    "Oración": oracion.strip(),
                    "Clasificación": clasificacion
                })
                vistos.add(forma)

    return [e for e in encontrados if e["Clasificación"] != "Imperativo"]

# --- Interfaz ---
uploaded_file = st.file_uploader("📤 Sube tu archivo .txt", type=["txt"])

if uploaded_file is not None:
    try:
        texto = uploaded_file.read().decode("utf-8")
        st.success("✅ Archivo cargado.")

        with st.expander("📄 Ver texto"):
            st.text(texto)

        verbos = detectar_subjuntivo(texto)

        if verbos:
            df = pd.DataFrame(verbos)
            st.subheader(f"🎉 Se encontraron {len(df)} formas verbales en subjuntivo")

            tab1, tab2, tab3 = st.tabs(["📊 Estadísticas", "📄 Texto resaltado", "📋 Detalles"])

            with tab1:
                fig = px.pie(df, names="Clasificación", title="Precisión por contexto")
                st.plotly_chart(fig)

                fig2 = px.pie(df, names="Tiempo", title="Distribución por tiempo")
                st.plotly_chart(fig2)

            with tab2:
                highlighted = texto
                for v in sorted(df["Verbo"].unique(), key=len, reverse=True):
                    highlighted = re.sub(
                        rf'\b({re.escape(v)})\b',
                        f'<mark style="background: #FFEB3B; padding: 2px 6px; border-radius: 4px;">\\1</mark>',
                        highlighted,
                        flags=re.IGNORECASE
                    )
                st.markdown(
                    f'<div style="line-height: 1.8; padding: 15px; background: #f8f9fa; border-radius: 8px;">{highlighted}</div>',
                    unsafe_allow_html=True
                )

            with tab3:
                st.dataframe(df, use_container_width=True)

            # Descarga CSV
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Descargar CSV",
                data=csv_data,
                file_name="subjuntivo_con_contexto.csv",
                mime="text/csv"
            )
        else:
            st.info("ℹ️ No se encontraron verbos en subjuntivo (o todos eran imperativos).")

    except Exception as e:
        st.error("❌ Error al procesar el archivo.")
        st.exception(e)
else:
    st.info("👈 Sube un archivo .txt para comenzar.")
