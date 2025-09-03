import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Configuración de la página
st.set_page_config(
    page_title="Analizador de Subjuntivo Español",
    page_icon="📝",
    layout="wide"
)

# Título y descripción
st.title("🔍 Analizador de Modo Subjuntivo en Español")
st.markdown("""
Esta aplicación identifica y analiza todas las formas verbales en modo subjuntivo 
en textos en español y genera un informe detallado en Excel.
""")

# Lista de terminaciones de verbos en subjuntivo
subjuntivo_terminaciones = [
    'ara', 'aras', 'áramos', 'aran',  # Pretérito imperfecto (-ar)
    'are', 'ares', 'áremos', 'aren',  # Futuro simple (-ar)
    'iera', 'ieras', 'iéramos', 'ieran',  # Pretérito imperfecto (-er/-ir)
    'iere', 'ieres', 'iéremos', 'ieren',  # Futuro simple (-er/-ir)
    'era', 'eras', 'éramos', 'eran',  # Variante (-er)
    'ese', 'eses', 'ésemos', 'esen',  # Pretérito imperfecto (variante)
    'a', 'as', 'amos', 'an',  # Presente (-ar)
    'e', 'es', 'emos', 'en',  # Presente (-er)
    'a', 'as', 'amos', 'an',  # Presente (-ir)
    'se', 'ses', 'semos', 'sen'  # Otra variante
]

# Verbos irregulares comunes en subjuntivo
verbos_irregulares_subjuntivo = [
    'sea', 'seas', 'seamos', 'sean',  # ser
    'vaya', 'vayas', 'vayamos', 'vayan',  # ir
    'haya', 'hayas', 'hayamos', 'hayan',  # haber
    'esté', 'estés', 'estemos', 'estén',  # estar
    'dé', 'des', 'demos', 'den',  # dar
    'sepa', 'sepas', 'sepamos', 'sepan',  # saber
    'quepa', 'quepas', 'quepamos', 'quepan'  # caber
]

# Conectores que suelen introducir subjuntivo
conectores_subjuntivo = [
    'que', 'cuando', 'si', 'aunque', 'para que', 'a fin de que', 
    'como si', 'a menos que', 'con tal de que', 'en caso de que',
    'sin que', 'antes de que', 'ojalá', 'espero que', 'dudo que',
    'no creo que', 'es posible que', 'es probable que'
]

def es_subjuntivo(palabra):
    """Determina si una palabra es un verbo en subjuntivo"""
    palabra = palabra.lower().strip('.,;:!?¿¡()[]{}"\'')
    
    # Verificar verbos irregulares
    if palabra in verbos_irregulares_subjuntivo:
        return True
    
    # Verificar por terminaciones
    for terminacion in subjuntivo_terminaciones:
        if palabra.endswith(terminacion):
            return True
    
    return False

def encontrar_clausula(texto, posicion_verbo):
    """Encuentra la cláusula que contiene el verbo en subjuntivo"""
    # Buscar hacia atrás para encontrar el inicio de la cláusula
    inicio = 0
    for conector in conectores_subjuntivo:
        idx = texto.rfind(conector, 0, posicion_verbo)
        if idx != -1 and idx > inicio:
            inicio = idx
    
    # Buscar hacia adelante para encontrar el final de la cláusula
    fin = len(texto)
    for puntuacion in ['.', '!', '?', ';']:
        idx = texto.find(puntuacion, posicion_verbo)
        if idx != -1 and idx < fin:
            fin = idx
    
    clausula = texto[inicio:fin].strip()
    return clausula

def analizar_texto(texto):
    """Analiza el texto y encuentra todos los verbos en subjuntivo"""
    palabras = texto.split()
    resultados = []
    
    for i, palabra in enumerate(palabras):
        if es_subjuntivo(palabra):
            # Encontrar la posición de la palabra en el texto original
            posicion = texto.find(palabra)
            
            # Encontrar la cláusula
            clausula = encontrar_clausula(texto, posicion)
            
            # Determinar tiempo verbal aproximado
            tiempo = determinar_tiempo_verbal(palabra)
            
            # Determinar persona y número
            persona = determinar_persona(palabra)
            
            resultados.append({
                'Verbo': palabra,
                'Tiempo': tiempo,
                'Persona': persona,
                'Cláusula': clausula,
                'Posición': f"Palabra {i+1}"
            })
    
    return resultados

def determinar_tiempo_verbal(verbo):
    """Determina el tiempo verbal aproximado basado en la terminación"""
    verbo = verbo.lower()
    
    if any(verbo.endswith(t) for t in ['a', 'as', 'amos', 'an', 'e', 'es', 'emos', 'en']):
        return 'Presente'
    elif any(verbo.endswith(t) for t in ['ara', 'aras', 'áramos', 'aran', 'iera', 'ieras', 'iéramos', 'ieran', 'era', 'eras', 'éramos', 'eran', 'ese', 'eses', 'ésemos', 'esen']):
        return 'Pretérito imperfecto'
    elif any(verbo.endswith(t) for t in ['are', 'ares', 'áremos', 'aren', 'iere', 'ieres', 'iéremos', 'ieren']):
        return 'Futuro simple'
    else:
        return 'Indeterminado'

def determinar_persona(verbo):
    """Determina la persona y número del verbo"""
    verbo = verbo.lower()
    
    if verbo.endswith(('o', 'a', 'e')):  # 1ra singular
        return '1ra persona singular'
    elif verbo.endswith(('as', 'es')):  # 2da singular
        return '2da persona singular'
    elif verbo.endswith(('a', 'e')):  # 3ra singular
        return '3ra persona singular'
    elif verbo.endswith(('amos', 'emos', 'imos')):  # 1ra plural
        return '1ra persona plural'
    elif verbo.endswith(('áis', 'éis', 'ís')):  # 2da plural
        return '2da persona plural'
    elif verbo.endswith(('an', 'en')):  # 3ra plural
        return '3ra persona plural'
    else:
        return 'Indeterminada'

def crear_excel(resultados):
    """Crea un archivo Excel con los resultados"""
    if not resultados:
        return None
    
    df = pd.DataFrame(resultados)
    
    # Crear el archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Subjuntivos', index=False)
        
        # Obtener el libro y la hoja de trabajo para aplicar formato
        workbook = writer.book
        worksheet = writer.sheets['Subjuntivos']
        
        # Formato para los encabezados
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#366092',
            'font_color': 'white',
            'border': 1
        })
        
        # Aplicar formato a los encabezados
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Ajustar el ancho de las columnas
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, max_len)
    
    output.seek(0)
    return output

# Sidebar con información
with st.sidebar:
    st.header("ℹ️ Información")
    st.markdown("""
    **Características:**
    - Identifica verbos en subjuntivo
    - Analiza tiempo y persona verbal
    - Extrae cláusulas completas
    - Genera informe en Excel
    
    **Ejemplos de subjuntivo:**
    - Es importante que **estudies**
    - Ojalá **llueva** mañana
    - Quiero que **vengas** pronto
    """)

# Área de texto para entrada
col1, col2 = st.columns([2, 1])

with col1:
    texto = st.text_area(
        "Introduce el texto a analizar:",
        height=300,
        placeholder="Ejemplo: Es necesario que estudies más para el examen. Ojalá que tengas suerte en tu viaje..."
    )

with col2:
    st.markdown("### 📊 Estadísticas")
    if texto:
        total_palabras = len(texto.split())
        st.metric("Palabras", total_palabras)
    else:
        st.info("Introduce texto para ver estadísticas")

# Botón para analizar
if st.button("🔍 Analizar Subjuntivo", type="primary"):
    if not texto.strip():
        st.warning("Por favor, introduce un texto para analizar.")
    else:
        with st.spinner("Analizando texto..."):
            resultados = analizar_texto(texto)
        
        if resultados:
            st.success(f"✅ Se encontraron {len(resultados)} verbos en subjuntivo")
            
            # Mostrar resultados en tabla
            st.subheader("📋 Resultados del Análisis")
            df = pd.DataFrame(resultados)
            st.dataframe(df, use_container_width=True)
            
            # Generar y descargar Excel
            excel_file = crear_excel(resultados)
            
            st.download_button(
                label="📥 Descargar Informe Excel",
                data=excel_file,
                file_name="analisis_subjuntivo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # Mostrar estadísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total subjuntivos", len(resultados))
            with col2:
                tiempos = df['Tiempo'].value_counts()
                st.metric("Tiempo más común", tiempos.index[0] if len(tiempos) > 0 else "N/A")
            with col3:
                st.metric("Verbos únicos", df['Verbo'].nunique())
            
        else:
            st.info("ℹ️ No se encontraron verbos en modo subjuntivo en el texto.")

# Ejemplos predefinidos
st.subheader("💡 Ejemplos para probar")
ejemplos = {
    "Ejemplo 1": "Es importante que estudies para el examen. Ojalá que tengas buena suerte.",
    "Ejemplo 2": "Quiero que vengas a la fiesta. Dudo que ella pueda asistir.",
    "Ejemplo 3": "Sería bueno que lloviera pronto. Temo que se sequen las plantas."
}

cols = st.columns(3)
for i, (nombre, ejemplo) in enumerate(ejemplos.items()):
    with cols[i]:
        if st.button(f"📌 {nombre}"):
            texto = ejemplo
            st.rerun()

# Información adicional
with st.expander("📚 Acerca del modo subjuntivo"):
    st.markdown("""
    El modo subjuntivo en español se utiliza para expresar:
    
    - **Deseos**: Ojalá que tengas suerte
    - **Dudas**: No creo que venga
    - **Emociones**: Me alegra que estés aquí
    - **Impersonalidad**: Es necesario que estudies
    - **Consejos**: Te sugiero que leas más
    - **Hipótesis**: Si tuviera dinero, viajaría
    
    Esta aplicación detecta las formas verbales más comunes del subjuntivo,
    pero puede haber casos complejos que requieran análisis manual.
    """)

# Pie de página
st.markdown("---")
st.caption("Analizador de Modo Subjuntivo v1.0 | Desarrollado con Streamlit")
