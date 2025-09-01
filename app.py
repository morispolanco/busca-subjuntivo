import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Configuración de la página
st.set_page_config(page_title="🔍 Subjuntivo Finder (con contexto)", layout="wide")
st.title("🔍 Buscador de Verbos en Subjuntivo con Análisis Contextual")
st.markdown("""
Esta app detecta verbos en modo subjuntivo **distinguiéndolos del imperativo**,
analizando **la forma verbal + su contexto gramatical**.
""")

# === BASE DE DATOS COMPLETA DE FORMAS EN SUBJUNTIVO ===
SUBJUNTIVO_COMPLETO = {
    # -AR
    "hable": "hablar", "hables": "hablar", "hable": "hablar", "hablemos": "hablar", "habléis": "hablar", "hablen": "hablar",
    "hablara": "hablar", "hablaras": "hablar", "hablara": "hablar", "habláramos": "hablar", "hablarais": "hablar", "hablaran": "hablar",
    "hablase": "hablar", "hablases": "hablar", "hablase": "hablar", "hablásemos": "hablar", "hablaseis": "hablar", "hablasen": "hablar",
    "hablare": "hablar", "hablares": "hablar", "hablare": "hablar", "habláremos": "hablar", "hablareis": "hablar", "hablaren": "hablar",

    # -ER
    "coma": "comer", "comas": "comer", "coma": "comer", "comamos": "comer", "comáis": "comer", "coman": "comer",
    "comiera": "comer", "comieras": "comer", "comiera": "comer", "comiéramos": "comer", "comierais": "comer", "comieran": "comer",
    "comiese": "comer", "comieses": "comer", "comiese": "comer", "comiésemos": "comer", "comieseis": "comer", "comiesen": "comer",
    "comiere": "comer", "comieres": "comer", "comiere": "comer", "comiéremos": "comer", "comiereis": "comer", "comieren": "comer",

    # -IR
    "viva": "vivir", "vivas": "vivir", "viva": "vivir", "vivamos": "vivir", "viváis": "vivir", "vivan": "vivir",
    "viviera": "vivir", "vivieras": "vivir", "viviera": "vivir", "viviéramos": "vivir", "vivierais": "vivir", "vivieran": "vivir",
    "viviese": "vivir", "vivieses": "vivir", "viviese": "vivir", "viviésemos": "vivir", "vivieseis": "vivir", "viviesen": "vivir",
    "viviere": "vivir", "vivieres": "vivir", "viviere": "vivir", "viviéremos": "vivir", "viviereis": "vivir", "vivieren": "vivir",

    # SER
    "sea": "ser", "seas": "ser", "sea": "ser", "seamos": "ser", "seáis": "ser", "sean": "ser",
    "fuera": "ser", "fueras": "ser", "fuera": "ser", "fuéramos": "ser", "fuerais": "ser", "fueran": "ser",
    "fuese": "ser", "fueses": "ser", "fuese": "ser", "fuésemos": "ser", "fueseis": "ser", "fuesen": "ser",
    "fuere": "ser", "fueres": "ser", "fuere": "ser", "fuéremos": "ser", "fuereis": "ser", "fueren": "ser",

    # ESTAR
    "esté": "estar", "estés": "estar", "esté": "estar", "estemos": "estar", "estéis": "estar", "estén": "estar",
    "estuviera": "estar", "estuvieras": "estar", "estuviera": "estar", "estuviéramos": "estar", "estuvierais": "estar", "estuvieran": "estar",
    "estuviese": "estar", "estuvieses": "estar", "estuviese": "estar", "estuviésemos": "estar", "estuvieseis": "estar", "estuviesen": "estar",
    "estuviere": "estar", "estuvieres": "estar", "estuviere": "estar", "estuviéremos": "estar", "estuviereis": "estar", "estuvieren": "estar",

    # HABER
    "haya": "haber", "hayas": "haber", "haya": "haber", "hayamos": "haber", "hayáis": "haber", "hayan": "haber",
    "hubiera": "haber", "hubieras": "haber", "hubiera": "haber", "hubiéramos": "haber", "hubierais": "haber", "hubieran": "haber",
    "hubiese": "haber", "hubieses": "haber", "hubiese": "haber", "hubiésemos": "haber", "hubieseis": "haber", "hubiesen": "haber",
    "hubiere": "haber", "hubieres": "haber", "hubiere": "haber", "hubiéremos": "haber", "hubiereis": "haber", "hubieren": "haber",

    # IR
    "vaya": "ir", "vayas": "ir", "vaya": "ir", "vayamos": "ir", "vayáis": "ir", "vayan": "ir",
    "fuera": "ir", "fueras": "ir", "fuera": "ir", "fuéramos": "ir", "fuerais": "ir", "fueran": "ir",
    "fuese": "ir", "fueses": "ir", "fuese": "ir", "fuésemos": "ir", "fueseis": "ir", "fuesen": "ir",
    "fuere": "ir", "fueres": "ir", "fuere": "ir", "fuéremos": "ir", "fuereis": "ir", "fueren": "ir",

    # DAR
    "dé": "dar", "des": "dar", "dé": "dar", "demos": "dar", "deis": "dar", "den": "dar",
    "diera": "dar", "dieras": "dar", "diera": "dar", "diéramos": "dar", "dierais": "dar", "dieran": "dar",
    "diese": "dar", "dieses": "dar", "diese": "dar", "diésemos": "dar", "dieseis": "dar", "diesen": "dar",
    "diere": "dar", "dieres": "dar", "diere": "dar", "diéremos": "dar", "diereis": "dar", "dieren": "dar",

    # PODER
    "pueda": "poder", "puedas": "poder", "pueda": "poder", "podamos": "poder", "podáis": "poder", "puedan": "poder",
    "pudiera": "poder", "pudieras": "poder", "pudiera": "poder", "pudiéramos": "poder", "pudierais": "poder", "pudieran": "poder",
    "pudiese": "poder", "pudieses": "poder", "pudiese": "poder", "pudiésemos": "poder", "pudieseis": "poder", "pudiesen": "poder",
    "pudiere": "poder", "pudieres": "poder", "pudiere": "poder", "pudiéremos": "poder", "pudiereis": "poder", "pudieren": "poder",

    # QUERER
    "quiera": "querer", "quieras": "querer", "quiera": "querer", "queramos": "querer", "queráis": "querer", "quieran": "querer",
    "quisiera": "querer", "quisieras": "querer", "quisiera": "querer", "quisiéramos": "querer", "quisierais": "querer", "quisieran": "querer",
    "quisiese": "querer", "quisieses": "querer", "quisiese": "querer", "quisiésemos": "querer", "quisieseis": "querer", "quisiesen": "querer",
    "quisiere": "querer", "quisieres": "querer", "quisiere": "querer", "quisiéremos": "querer", "quisiereis": "querer", "quisieren": "querer",

    # HACER
    "haga": "hacer", "hagas": "hacer", "haga": "hacer", "hagamos": "hacer", "hagáis": "hacer", "hagan": "hacer",
    "hiciera": "hacer", "hicieras": "hacer", "hiciera": "hacer", "hiciéramos": "hacer", "hicierais": "hacer", "hicieran": "hacer",
    "hiciese": "hacer", "hicieses": "hacer", "hiciese": "hacer", "hiciésemos": "hacer", "hicieseis": "hacer", "hiciesen": "hacer",
    "hicere": "hacer", "hiceres": "hacer", "hicere": "hacer", "hiciéremos": "hacer", "hicereis": "hacer", "hiceren": "hacer",

    # VENIR
    "venga": "venir", "vengas": "venir", "venga": "venir", "vengamos": "venir", "vengáis": "venir", "vengan": "venir",
    "viniera": "venir", "vinieras": "venir", "viniera": "venir", "viniéramos": "venir", "vinierais": "venir", "vinieran": "venir",
    "viniese": "venir", "vinieses": "venir", "viniese": "venir", "viniésemos": "venir", "vinieseis": "venir", "viniesen": "venir",
    "viniere": "venir", "vinieres": "venir", "viniere": "venir", "viniéremos": "venir", "viniereis": "venir", "vinieren": "venir",

    # VALER
    "valga": "valer", "valgas": "valer", "valga": "valer", "valgamos": "valer", "valgáis": "valer", "valgan": "valer",
    "valiera": "valer", "valieras": "valer", "valiera": "valer", "valiéramos": "valer", "valierais": "valer", "valieran": "valer",
    "valiese": "valer", "valieses": "valer", "valiese": "valer", "valiésemos": "valer", "valieseis": "valer", "valiesen": "valer",
    "valiere": "valer", "valieres": "valer", "valiere": "valer", "valiéremos": "valer", "valiereis": "valer", "valieren": "valer",

    # CABER
    "quepa": "caber", "quepas": "caber", "quepa": "caber", "quepamos": "caber", "quepáis": "caber", "quepan": "caber",
    "cupiera": "caber", "cupieras": "caber", "cupiera": "caber", "cupiéramos": "caber", "cupieras": "caber", "cupieran": "caber",
    "cupiese": "caber", "cupieses": "caber", "cupiese": "caber", "cupiésemos": "caber", "cupieseis": "caber", "cupiesen": "caber",
    "cupiere": "caber", "cupieres": "caber", "cupiere": "caber", "cupiéremos": "caber", "cupiereis": "caber", "cupieren": "caber",

    # DORMIR
    "duerma": "dormir", "duermas": "dormir", "duerma": "dormir", "durmamos": "dormir", "durmáis": "dormir", "duerman": "dormir",
    "durmiera": "dormir", "durmieras": "dormir", "durmiera": "dormir", "durmiéramos": "dormir", "durmieras": "dormir", "durmieran": "dormir",
    "durmiese": "dormir", "durmieses": "dormir", "durmiese": "dormir", "durmiésemos": "dormir", "durmieseis": "dormir", "durmiesen": "dormir",

    # PEDIR
    "pida": "pedir", "pidas": "pedir", "pida": "pedir", "pidamos": "pedir", "pidáis": "pedir", "pidan": "pedir",
    "pidiera": "pedir", "pidieras": "pedir", "pidiera": "pedir", "pidiéramos": "pedir", "pidieras": "pedir", "pidieran": "pedir",
    "pidiese": "pedir", "pidieses": "pedir", "pidiese": "pedir", "pidiésemos": "pedir", "pidieseis": "pedir", "pidiesen": "pedir",

    # REÍR
    "ría": "reír", "rías": "reír", "ría": "reír", "riamos": "reír", "riáis": "reír", "rían": "reír",
    "riera": "reír", "rieras": "reír", "riera": "reír", "riéramos": "reír", "rieras": "reír", "rieran": "reír",
    "riese": "reír", "rieses": "reír", "riese": "reír", "riésemos": "reír", "rieseis": "reír", "riesen": "reír",

    # LEER
    "lea": "leer", "leas": "leer", "lea": "leer", "leamos": "leer", "leáis": "leer", "lean": "leer",
    "leyera": "leer", "leyeras": "leer", "leyera": "leer", "leyéramos": "leer", "leyeras": "leer", "leyeran": "leer",
    "leyese": "leer", "leyeses": "leer", "leyese": "leer", "leyésemos": "leer", "leyeseis": "leer", "leyesen": "leer",

    # CAER
    "caiga": "caer", "caigas": "caer", "caiga": "caer", "caigamos": "caer", "caigáis": "caer", "caigan": "caer",
    "cayera": "caer", "cayeras": "caer", "cayera": "caer", "cayéramos": "caer", "cayeras": "caer", "cayeran": "caer",
    "cayese": "caer", "cayeses": "caer", "cayese": "caer", "cayésemos": "caer", "cayeseis": "caer", "cayesen": "caer",

    # CONSTRUIR
    "construya": "construir", "construyas": "construir", "construya": "construir", "construyamos": "construir", "construyáis": "construir", "construyan": "construir",
    "construyera": "construir", "construyeras": "construir", "construyera": "construir", "construyéramos": "construir", "construyeras": "construir", "construyeran": "construir",
    "construyese": "construir", "construyeses": "construir", "construyese": "construir", "construyésemos": "construir", "construyeseis": "construir", "construyesen": "construir",

    # ADQUIRIR
    "adquiera": "adquirir", "adquieras": "adquirir", "adquiera": "adquirir", "adquiramos": "adquirir", "adquiráis": "adquirir", "adquieran": "adquirir",
    "adquiriera": "adquirir", "adquirieras": "adquirir", "adquiriera": "adquirir", "adquiriéramos": "adquirir", "adquirieras": "adquirir", "adquirieran": "adquirir",
    "adquiriese": "adquirir", "adquierieses": "adquirir", "adquiriese": "adquirir", "adquiriésemos": "adquirir", "adquirieseis": "adquirir", "adquieriesen": "adquirir",

    # INCLUIR
    "incluya": "incluir", "incluyas": "incluir", "incluya": "incluir", "incluyamos": "incluir", "incluyáis": "incluir", "incluyan": "incluir",
    "incluyera": "incluir", "incluyeras": "incluir", "incluyera": "incluir", "incluyéramos": "incluir", "incluyeras": "incluir", "incluyeran": "incluir",
    "incluyese": "incluir", "incluyeses": "incluir", "incluyese": "incluir", "incluyésemos": "incluir", "incluyeseis": "incluir", "incluyesen": "incluir",

    # ATRIBUIR
    "atribuya": "atribuir", "atribuyas": "atribuir", "atribuya": "atribuir", "atribuyamos": "atribuir", "atribuyáis": "atribuir", "atribuyan": "atribuir",
    "atribuyera": "atribuir", "atribuyeras": "atribuir", "atribuyera": "atribuir", "atribuyéramos": "atribuir", "atribuyeras": "atribuir", "atribuyeran": "atribuir",
    "atribuyese": "atribuir", "atribuyeses": "atribuir", "atribuyese": "atribuir", "atribuyésemos": "atribuir", "atribuyeseis": "atribuir", "atribuyesen": "atribuir",

    # PROVEER
    "provea": "proveer", "proveas": "proveer", "provea": "proveer", "proveamos": "proveer", "proveáis": "proveer", "provean": "proveer",
    "proveyera": "proveer", "proveyeras": "proveer", "proveyera": "proveer", "proveyéramos": "proveer", "proveyeras": "proveer", "proveyeran": "proveer",
    "proveyese": "proveer", "proveyeses": "proveer", "proveyese": "proveer", "proveyésemos": "proveer", "proveyeseis": "proveer", "proveyesen": "proveer",

    # DESLEER
    "deslea": "desleer", "desleas": "desleer", "deslea": "desleer", "desleamos": "desleer", "desleáis": "desleer", "deslean": "desleer",
    "desleyera": "desleer", "desleyeras": "desleer", "desleyera": "desleer", "desleyéramos": "desleer", "desleyeras": "desleer", "desleyeran": "desleer",
    "desleyese": "desleer", "desleyeses": "desleer", "desleyese": "desleer", "desleyésemos": "desleer", "desleyeseis": "desleer", "desleyesen": "desleer",

    # CUMPLIR
    "cumpla": "cumplir", "cumplas": "cumplir", "cumpla": "cumplir", "cumplamos": "cumplir", "cumpláis": "cumplir", "cumplan": "cumplir",
    "cumpliera": "cumplir", "cumplieras": "cumplir", "cumpliera": "cumplir", "cumpliéramos": "cumplir", "cumplieras": "cumplir", "cumplieran": "cumplir",
    "cumpliese": "cumplir", "cumplieses": "cumplir", "cumpliese": "cumplir", "cumpliésemos": "cumplir", "cumplieseis": "cumplir", "cumpliesen": "cumplir",

    # SONREÍR
    "sonría": "sonreír", "sonrías": "sonreír", "sonría": "sonreír", "sonriamos": "sonreír", "sonriáis": "sonreír", "sonrían": "sonreír",
    "sonriera": "sonreír", "sonrieras": "sonreír", "sonriera": "sonreír", "sonriéramos": "sonreír", "sonrieras": "sonreír", "sonrieran": "sonreír",
    "sonriese": "sonreír", "sonrieses": "sonreír", "sonriese": "sonreír", "sonriésemos": "sonreír", "sonrieseis": "sonreír", "sonriesen": "sonreír",

    # DESOÍR
    "desoiga": "desoír", "desoigas": "desoír", "desoiga": "desoír", "desoigamos": "desoír", "desoigáis": "desoír", "desoigan": "desoír",
    "desoyera": "desoír", "desoyeran": "desoír", "desoyera": "desoír", "desoyéramos": "desoír", "desoyeran": "desoír", "desoyeran": "desoír",
    "desoyese": "desoír", "desoyses": "desoír", "desoyese": "desoír", "desoyésemos": "desoír", "desoyeseis": "desoír", "desoysen": "desoír",

    # PERCIBIR
    "perciba": "percibir", "percibas": "percibir", "perciba": "percibir", "percibamos": "percibir", "percibáis": "percibir", "perciban": "percibir",
    "percibiera": "percibir", "percibieras": "percibir", "percibiera": "percibir", "percibiéramos": "percibir", "percibieras": "percibir", "percibieran": "percibir",
    "percibiese": "percibir", "percibieses": "percibir", "percibiese": "percibir", "percibiésemos": "percibir", "percibieseis": "percibir", "percibiesen": "percibir",

    # ELEGIR
    "elija": "elegir", "elijas": "elegir", "elija": "elegir", "elijamos": "elegir", "elijáis": "elegir", "elijan": "elegir",
    "eligiera": "elegir", "eligieras": "elegir", "eligiera": "elegir", "eligieran": "elegir", "eligiera": "elegir", "eligieran": "elegir",
    "eligiese": "elegir", "eligieses": "elegir", "eligiese": "elegir", "eligiese": "elegir", "eligieseis": "elegir", "eligiesen": "elegir",
}

# Conjunto para búsquedas rápidas
SUBJ_SET = set(SUBJUNTIVO_COMPLETO.keys())

# === EXPRESIONES QUE INTRODUCEN SUBJUNTIVO ===
TRIGGERS_SUBJUNTIVO = [
    r'\bque\b', r'\baunque\b', r'\ba pesar de que\b', r'\bcomo si\b',
    r'\bantes de que\b', r'\bhasta que\b', r'\bdespués de que\b', r'\bpara que\b',
    r'\bno creo que\b', r'\bdudo que\b', r'\bes importante que\b',
    r'\bes necesario que\b', r'\bes bueno que\b', r'\bme alegra que\b',
    r'\blo siento que\b', r'\bme sorprende que\b', r'\bojalá\b', r'\bojalá que\b',
    r'\bquizá(s)?\b', r'\bquizá(s)? que\b', r'\btal vez\b', r'\bsin que\b',
    r'\bsalvo que\b', r'\bexcepto que\b', r'\ba menos que\b', r'\ben caso de que\b',
    r'\bsiempre que\b', r'\bcuando\b', r'\bmientras que\b', r'\bpor mucho que\b',
]

# === EXPRESIONES QUE INDICAN IMPERATIVO ===
TRIGGERS_IMPERATIVO = [
    r'\busted\b', r'\bus\.t\.\b', r'\bu[ds]t[ed]d\b', r'\bpor favor\b', r'\bporfa\b', r'\bporfi\b',
    r'^¡', r'!$', r'\bordena\b', r'\bmandato\b', r'\bimperativo\b'
]

# === Funciones de contexto ===
def get_context(sentence, verb_start):
    before = sentence[:verb_start].strip()
    after = sentence[verb_start:].strip()
    return before, after

def is_subjunctive_context(before, after):
    full = (before + " " + after).lower()
    return any(re.search(trigger, full) for trigger in TRIGGERS_SUBJUNTIVO)

def is_imperative_context(before, after):
    full = (before + " " + after).lower()
    return any(re.search(trigger, full) for trigger in TRIGGERS_IMPERATIVO)

# === Detector principal ===
def detectar_subjuntivo(texto):
    oraciones = re.split(r'[.!?]+', texto)
    encontrados = []
    vistos = set()

    for oracion in oraciones:
        oracion = oracion.strip()
        if not oracion:
            continue

        palabras = re.findall(r'\b\w+\b', oracion)
        for palabra in palabras:
            forma = palabra.lower()
            if forma not in SUBJ_SET or forma in vistos:
                continue

            match = re.search(r'\b' + re.escape(palabra) + r'\b', oracion, re.IGNORECASE)
            if not match:
                continue
            pos = match.start()

            before, after = get_context(oracion, pos)
            es_subj = is_subjunctive_context(before, after)
            es_imp = is_imperative_context(before, after)

            if es_imp and not es_subj:
                continue  # Es imperativo, ignorar

            tiempo = ("Imperfecto" if re.search(r'(ra|se|ramos|semos|rais|seis|ran|sen)$', forma)
                      else "Futuro" if forma.endswith('re')
                      else "Presente")

            numero = "Plural" if forma.endswith(("mos", "is", "n", "áis", "ais")) else "Singular"

            encontrados.append({
                "Verbo": palabra,
                "Lema": SUBJUNTIVO_COMPLETO[forma],
                "Tiempo": tiempo,
                "Modo": "Subjuntivo",
                "Número": numero,
                "Oración": oracion,
                "Clasificación": "Seguro" if es_subj else "Posible"
            })
            vistos.add(forma)

    return encontrados

# --- Interfaz Streamlit ---
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
            st.subheader(f"🎉 Se encontraron {len(df)} verbos en subjuntivo")

            tab1, tab2, tab3 = st.tabs(["📊 Estadísticas", "📄 Texto resaltado", "📋 Detalles"])

            with tab1:
                fig1 = px.pie(df, names="Clasificación", title="Clasificación por contexto")
                st.plotly_chart(fig1)
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
            st.info("ℹ️ No se encontraron verbos en subjuntivo (o eran imperativos).")

    except Exception as e:
        st.error("❌ Error al procesar el archivo.")
        st.exception(e)
else:
    st.info("👈 Sube un archivo .txt para comenzar.")
