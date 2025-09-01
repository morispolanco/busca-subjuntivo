import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Configuración de la página
st.set_page_config(page_title="🔍 Subjuntivo Finder (Completo)", layout="wide")
st.title("🔍 Buscador de Verbos en Modo Subjuntivo")
st.markdown("""
Esta app detecta **todas las formas verbales en modo subjuntivo** en un texto en español,
usando una base de datos completa de conjugaciones.
""")

# === BASE DE DATOS COMPLETA DE FORMAS EN SUBJUNTIVO ===
SUBJUNTIVO_COMPLETO = {
    # -----------------------------------------------------------------------
    # VERBOS REGULARES
    # -----------------------------------------------------------------------

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

    # -----------------------------------------------------------------------
    # VERBOS IRREGULARES Y ESPECIALES
    # -----------------------------------------------------------------------

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

    # SABER
    "sepa": "saber", "sepas": "saber", "sepa": "saber", "sepamos": "saber", "sepáis": "saber", "sepan": "saber",
    "supiera": "saber", "supieras": "saber", "supiera": "saber", "supiéramos": "saber", "supierais": "saber", "supieran": "saber",
    "supiese": "saber", "supieses": "saber", "supiese": "saber", "supiésemos": "saber", "supieseis": "saber", "supiesen": "saber",
    "supiere": "saber", "supieres": "saber", "supiere": "saber", "supiéremos": "saber", "supiereis": "saber", "supieren": "saber",

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

    # DECIR
    "diga": "decir", "digas": "decir", "diga": "decir", "digamos": "decir", "digáis": "decir", "digan": "decir",
    "dijera": "decir", "dijeras": "decir", "dijera": "decir", "dijéramos": "decir", "dijerais": "decir", "dijeran": "decir",
    "dijese": "decir", "dijeses": "decir", "dijese": "decir", "dijésemos": "decir", "dijeseis": "decir", "dijesen": "decir",
    "dijere": "decir", "dijeres": "decir", "dijere": "decir", "dijéremos": "decir", "dijereis": "decir", "dijeren": "decir",

    # VENIR
    "venga": "venir", "vengas": "venir", "venga": "venir", "vengamos": "venir", "vengáis": "venir", "vengan": "venir",
    "viniera": "venir", "vinieras": "venir", "viniera": "venir", "viniéramos": "venir", "vinierais": "venir", "vinieran": "venir",
    "viniese": "venir", "vinieses": "venir", "viniese": "venir", "viniésemos": "venir", "vinieseis": "venir", "viniesen": "venir",
    "viniere": "venir", "vinieres": "venir", "viniere": "venir", "viniéremos": "venir", "viniereis": "venir", "vinieren": "venir",

    # PONER
    "ponga": "poner", "pongas": "poner", "ponga": "poner", "pongamos": "poner", "pongáis": "poner", "pongan": "poner",
    "pusiera": "poner", "pusieras": "poner", "pusiera": "poner", "pusiéramos": "poner", "pusierais": "poner", "pusieran": "poner",
    "pusiese": "poner", "pusieses": "poner", "pusiese": "poner", "pusiésemos": "poner", "pusieseis": "poner", "pusiesen": "poner",
    "pusiere": "poner", "pusieres": "poner", "pusiere": "poner", "pusiéremos": "poner", "pusiereis": "poner", "pusieren": "poner",

    # SALIR
    "salga": "salir", "salgas": "salir", "salga": "salir", "salgamos": "salir", "salgáis": "salir", "salgan": "salir",
    "saliera": "salir", "salieras": "salir", "saliera": "salir", "saliéramos": "salir", "salierais": "salir", "salieran": "salir",
    "saliese": "salir", "salieses": "salir", "saliese": "salir", "saliésemos": "salir", "salieseis": "salir", "saliesen": "salir",
    "salieres": "salir", "salieres": "salir", "salieres": "salir", "saliéremos": "salir", "salieres": "salir", "salieres": "salir",

    # TRAER
    "traiga": "traer", "traigas": "traer", "traiga": "traer", "traigamos": "traer", "traigáis": "traer", "traigan": "traer",
    "trajera": "traer", "trajeras": "traer", "trajera": "traer", "trajéramos": "traer", "trajerais": "traer", "trajeran": "traer",
    "trajese": "traer", "trajeses": "traer", "trajese": "traer", "trajésemos": "traer", "trajeseis": "traer", "trajesen": "traer",
    "trajere": "traer", "trajeres": "traer", "trajere": "traer", "trajéremos": "traer", "trajereis": "traer", "trajeren": "traer",

    # VALER
    "valga": "valer", "valgas": "valer", "valga": "valer", "valgamos": "valer", "valgáis": "valer", "valgan": "valer",
    "valiera": "valer", "valieras": "valer", "valiera": "valer", "valiéramos": "valer", "valierais": "valer", "valieran": "valer",
    "valiese": "valer", "valieses": "valer", "valiese": "valer", "valiésemos": "valer", "valieseis": "valer", "valiesen": "valer",
    "valiere": "valer", "valieres": "valer", "valiere": "valer", "valiéremos": "valer", "valiereis": "valer", "valieren": "valer",

    # MOVER
    "mueva": "mover", "muevas": "mover", "mueva": "mover", "movamos": "mover", "mováis": "mover", "muevan": "mover",
    "moviera": "mover", "movieras": "mover", "moviera": "mover", "moviéramos": "mover", "movierais": "mover", "movieran": "mover",
    "moviese": "mover", "movieses": "mover", "moviese": "mover", "moviésemos": "mover", "movieseis": "mover", "moviesen": "mover",
    "moviere": "mover", "movieres": "mover", "moviere": "mover", "moviéremos": "mover", "moviereis": "mover", "movieren": "mover",

    # OÍR
    "oiga": "oír", "oigas": "oír", "oiga": "oír", "oigamos": "oír", "oigáis": "oír", "oigan": "oír",
    "oyera": "oír", "oyeran": "oír", "oyera": "oír", "oyéramos": "oír", "oyeran": "oír", "oyeran": "oír",
    "oyese": "oír", "oyses": "oír", "oyese": "oír", "oyésemos": "oír", "oyeseis": "oír", "oysen": "oír",
    "oyere": "oír", "oyeres": "oír", "oyere": "oír", "oyéremos": "oír", "oyereis": "oír", "oyeren": "oír",

    # CUBRIR
    "cubra": "cubrir", "cubras": "cubrir", "cubra": "cubrir", "cubramos": "cubrir", "cubráis": "cubrir", "cubran": "cubrir",
    "cubriera": "cubrir", "cubrieras": "cubrir", "cubriera": "cubrir", "cubriéramos": "cubrir", "cubrieras": "cubrir", "cubrieran": "cubrir",
    "cubriese": "cubrir", "cubrieses": "cubrir", "cubriese": "cubrir", "cubriésemos": "cubrir", "cubrieseis": "cubrir", "cubriesen": "cubrir",
    "cubriere": "cubrir", "cubrieres": "cubrir", "cubriere": "cubrir", "cubriéremos": "cubrir", "cubriereis": "cubrir", "cubrieren": "cubrir",

    # CABER
    "quepa": "caber", "quepas": "caber", "quepa": "caber", "quepamos": "caber", "quepáis": "caber", "quepan": "caber",
    "cupiera": "caber", "cupieras": "caber", "cupiera": "caber", "cupiéramos": "caber", "cupieras": "caber", "cupieran": "caber",
    "cupiese": "caber", "cupieses": "caber", "cupiese": "caber", "cupiésemos": "caber", "cupieseis": "caber", "cupiesen": "caber",
    "cupiere": "caber", "cupieres": "caber", "cupiere": "caber", "cupiéremos": "caber", "cupiereis": "caber", "cupieren": "caber",

    # CONVENIR
    "convenza": "convencer", "convenzas": "convencer", "convenza": "convencer", "convenzamos": "convencer", "convenzáis": "convencer", "convenzan": "convencer",
    "conviniere": "convencer", "conviniere": "convencer", "conviniere": "convencer", "conviniéramos": "convencer", "conviniereis": "convencer", "conviniere": "convencer",

    # DORMIR
    "duerma": "dormir", "duermas": "dormir", "duerma": "dormir", "durmamos": "dormir", "durmáis": "dormir", "duerman": "dormir",
    "durmiera": "dormir", "durmieras": "dormir", "durmiera": "dormir", "durmiéramos": "dormir", "durmieras": "dormir", "durmieran": "dormir",
    "durmiese": "dormir", "durmieses": "dormir", "durmiese": "dormir", "durmiésemos": "dormir", "durmieseis": "dormir", "durmiesen": "dormir",
    "durmieres": "dormir", "durmieres": "dormir", "durmieres": "dormir", "durmiéremos": "dormir", "durmieres": "dormir", "durmieres": "dormir",

    # PEDIR
    "pida": "pedir", "pidas": "pedir", "pida": "pedir", "pidamos": "pedir", "pidáis": "pedir", "pidan": "pedir",
    "pidiera": "pedir", "pidieras": "pedir", "pidiera": "pedir", "pidiéramos": "pedir", "pidieras": "pedir", "pidieran": "pedir",
    "pidiese": "pedir", "pidieses": "pedir", "pidiese": "pedir", "pidiésemos": "pedir", "pidieseis": "pedir", "pidiesen": "pedir",
    "pidiere": "pedir", "pidieres": "pedir", "pidiere": "pedir", "pidiéremos": "pedir", "pidiereis": "pedir", "pidieren": "pedir",

    # SENTIR
    "sienta": "sentir", "sientas": "sentir", "sienta": "sentir", "sintamos": "sentir", "sintáis": "sentir", "sientan": "sentir",
    "sintiera": "sentir", "sintieras": "sentir", "sintiera": "sentir", "sintiéramos": "sentir", "sintieras": "sentir", "sintieran": "sentir",
    "sintiese": "sentir", "sintieses": "sentir", "sintiese": "sentir", "sintiésemos": "sentir", "sintieseis": "sentir", "sintiesen": "sentir",
    "sintiere": "sentir", "sintieres": "sentir", "sintiere": "sentir", "sintiéremos": "sentir", "sintiereis": "sentir", "sintieren": "sentir",

    # REÍR
    "ría": "reír", "rías": "reír", "ría": "reír", "riamos": "reír", "riáis": "reír", "rían": "reír",
    "riera": "reír", "rieras": "reír", "riera": "reír", "riéramos": "reír", "rieras": "reír", "rieran": "reír",
    "riese": "reír", "rieses": "reír", "riese": "reír", "riésemos": "reír", "rieseis": "reír", "riesen": "reír",
    "riere": "reír", "rieres": "reír", "riere": "reír", "riéremos": "reír", "riereis": "reír", "rieren": "reír",

    # LEER
    "lea": "leer", "leas": "leer", "lea": "leer", "leamos": "leer", "leáis": "leer", "lean": "leer",
    "leyera": "leer", "leyeras": "leer", "leyera": "leer", "leyéramos": "leer", "leyeras": "leer", "leyeran": "leer",
    "leyese": "leer", "leyeses": "leer", "leyese": "leer", "leyésemos": "leer", "leyeseis": "leer", "leyesen": "leer",
    "leyere": "leer", "leyeres": "leer", "leyere": "leer", "leyéremos": "leer", "leyereis": "leer", "leyeren": "leer",

    # CAER
    "caiga": "caer", "caigas": "caer", "caiga": "caer", "caigamos": "caer", "caigáis": "caer", "caigan": "caer",
    "cayera": "caer", "cayeras": "caer", "cayera": "caer", "cayéramos": "caer", "cayeras": "caer", "cayeran": "caer",
    "cayese": "caer", "cayeses": "caer", "cayese": "caer", "cayésemos": "caer", "cayeseis": "caer", "cayesen": "caer",
    "cayere": "caer", "cayeres": "caer", "cayere": "caer", "cayéremos": "caer", "cayereis": "caer", "cayeren": "caer",

    # ANDAR
    "ande": "andar", "andes": "andar", "ande": "andar", "andemos": "andar", "andéis": "andar", "anden": "andar",
    "anduviera": "andar", "anduvieras": "andar", "anduviera": "andar", "anduviéramos": "andar", "anduvieras": "andar", "anduvieran": "andar",
    "anduviese": "andar", "anduvieses": "andar", "anduviese": "andar", "anduviésemos": "andar", "anduvieseis": "andar", "anduviesen": "andar",
    "anduviere": "andar", "anduvieres": "andar", "anduviere": "andar", "anduviéremos": "andar", "anduviereis": "andar", "anduvieren": "andar",

    # TENER
    "tenga": "tener", "tengas": "tener", "tenga": "tener", "tengamos": "tener", "tengáis": "tener", "tengan": "tener",
    "tuviera": "tener", "tuvieras": "tener", "tuviera": "tener", "tuvieran": "tener", "tuviera": "tener", "tuvieran": "tener",
    "tuviese": "tener", "tuvieses": "tener", "tuviese": "tener", "tuviese": "tener", "tuvieseis": "tener", "tuviesen": "tener",
    "tuviere": "tener", "tuvieres": "tener", "tuviere": "tener", "tuviéremos": "tener", "tuviereis": "tener", "tuvieren": "tener",

    # MANTENER
    "mantenga": "mantener", "mantengas": "mantener", "mantenga": "mantener", "mantengamos": "mantener", "mantengáis": "mantener", "mantengan": "mantener",
    "mantuviera": "mantener", "mantuvieras": "mantener", "mantuviera": "mantener", "mantuviéramos": "mantener", "mantuvieras": "mantener", "mantuvieran": "mantener",
    "mantuviese": "mantener", "mantuvieses": "mantener", "mantuviese": "mantener", "mantuviésemos": "mantener", "mantuvieseis": "mantener", "mantuviesen": "mantener",
    "mantuviere": "mantener", "mantuvieres": "mantener", "mantuviere": "mantener", "mantuviéremos": "mantener", "mantuviereis": "mantener", "mantuvieren": "mantener",

    # CONTENER
    "contenga": "contener", "contengas": "contener", "contenga": "contener", "contengamos": "contener", "contengáis": "contener", "contengan": "contener",
    "contuviera": "contener", "contuvieras": "contener", "contuviera": "contener", "contuvieran": "contener", "contuviera": "contener", "contuvieran": "contener",
    "contuviese": "contener", "contuvieses": "contener", "contuviese": "contener", "contuviese": "contener", "contuvieseis": "contener", "contuviesen": "contener",
    "contuviere": "contener", "contuvieres": "contener", "contuviere": "contener", "contuviéremos": "contener", "contuviereis": "contener", "contuvieren": "contener",

    # ENTENDER
    "entienda": "entender", "entiendas": "entender", "entienda": "entender", "entendamos": "entender", "entendáis": "entender", "entiendan": "entender",
    "entendiera": "entender", "entendieras": "entender", "entendiera": "entender", "entendiéramos": "entender", "entendieras": "entender", "entendieran": "entender",
    "entendiese": "entender", "entendieses": "entender", "entendiese": "entender", "entendiésemos": "entender", "entendieseis": "entender", "entendiesen": "entender",
    "entendiere": "entender", "entendieres": "entender", "entendiere": "entender", "entendiéremos": "entender", "entendiereis": "entender", "entendieren": "entender",

    # HUIR
    "huya": "huir", "huyas": "huir", "huya": "huir", "huyamos": "huir", "huyáis": "huir", "huyan": "huir",
    "huyera": "huir", "huyeras": "huir", "huyera": "huir", "huyéramos": "huir", "huyeras": "huir", "huyeran": "huir",
    "huyese": "huir", "huyeses": "huir", "huyese": "huir", "huyésemos": "huir", "huyeseis": "huir", "huyesen": "huir",
    "huyere": "huir", "huyeres": "huir", "huyere": "huir", "huyéremos": "huir", "huyereis": "huir", "huyeren": "huir",

    # CONSTRUIR
    "construya": "construir", "construyas": "construir", "construya": "construir", "construyamos": "construir", "construyáis": "construir", "construyan": "construir",
    "construyera": "construir", "construyeras": "construir", "construyera": "construir", "construyéramos": "construir", "construyeras": "construir", "construyeran": "construir",
    "construyese": "construir", "construyeses": "construir", "construyese": "construir", "construyésemos": "construir", "construyeseis": "construir", "construyesen": "construir",
    "construyere": "construir", "construyeres": "construir", "construyere": "construir", "construyéremos": "construir", "construyereis": "construir", "construyeren": "construir",

    # ADQUIRIR
    "adquiera": "adquirir", "adquieras": "adquirir", "adquiera": "adquirir", "adquiramos": "adquirir", "adquiráis": "adquirir", "adquieran": "adquirir",
    "adquiriera": "adquirir", "adquirieras": "adquirir", "adquiriera": "adquirir", "adquiriéramos": "adquirir", "adquirieras": "adquirir", "adquirieran": "adquirir",
    "adquiriese": "adquirir", "adquierieses": "adquirir", "adquiriese": "adquirir", "adquiriésemos": "adquirir", "adquirieseis": "adquirir", "adquieriesen": "adquirir",
    "adquiriere": "adquirir", "adquierieres": "adquirir", "adquiriere": "adquirir", "adquiriéremos": "adquirir", "adquiriereis": "adquirir", "adquirieren": "adquirir",

    # INCLUIR
    "incluya": "incluir", "incluyas": "incluir", "incluya": "incluir", "incluyamos": "incluir", "incluyáis": "incluir", "incluyan": "incluir",
    "incluyera": "incluir", "incluyeras": "incluir", "incluyera": "incluir", "incluyéramos": "incluir", "incluyeras": "incluir", "incluyeran": "incluir",
    "incluyese": "incluir", "incluyeses": "incluir", "incluyese": "incluir", "incluyésemos": "incluir", "incluyeseis": "incluir", "incluyesen": "incluir",
    "incluyere": "incluir", "incluyeres": "incluir", "incluyere": "incluir", "incluyéremos": "incluir", "incluyereis": "incluir", "incluyeren": "incluir",

    # ATRIBUIR
    "atribuya": "atribuir", "atribuyas": "atribuir", "atribuya": "atribuir", "atribuyamos": "atribuir", "atribuyáis": "atribuir", "atribuyan": "atribuir",
    "atribuyera": "atribuir", "atribuyeras": "atribuir", "atribuyera": "atribuir", "atribuyéramos": "atribuir", "atribuyeras": "atribuir", "atribuyeran": "atribuir",
    "atribuyese": "atribuir", "atribuyeses": "atribuir", "atribuyese": "atribuir", "atribuyésemos": "atribuir", "atribuyeseis": "atribuir", "atribuyesen": "atribuir",
    "atribuyere": "atribuir", "atribuyeres": "atribuir", "atribuyere": "atribuir", "atribuyéremos": "atribuir", "atribuyereis": "atribuir", "atribuyeren": "atribuir",

    # PROVEER
    "provea": "proveer", "proveas": "proveer", "provea": "proveer", "proveamos": "proveer", "proveáis": "proveer", "provean": "proveer",
    "proveyera": "proveer", "proveyeras": "proveer", "proveyera": "proveer", "proveyéramos": "proveer", "proveyeras": "proveer", "proveyeran": "proveer",
    "proveyese": "proveer", "proveyeses": "proveer", "proveyese": "proveer", "proveyésemos": "proveer", "proveyeseis": "proveer", "proveyesen": "proveer",
    "proveyere": "proveer", "proveyeres": "proveer", "proveyere": "proveer", "proveyéremos": "proveer", "proveyereis": "proveer", "proveyeren": "proveer",

    # DESLEER
    "deslea": "desleer", "desleas": "desleer", "deslea": "desleer", "desleamos": "desleer", "desleáis": "desleer", "deslean": "desleer",
    "desleyera": "desleer", "desleyeras": "desleer", "desleyera": "desleer", "desleyéramos": "desleer", "desleyeras": "desleer", "desleyeran": "desleer",
    "desleyese": "desleer", "desleyeses": "desleer", "desleyese": "desleer", "desleyésemos": "desleer", "desleyeseis": "desleer", "desleyesen": "desleer",
    "desleyere": "desleer", "desleyeres": "desleer", "desleyere": "desleer", "desleyéremos": "desleer", "desleyereis": "desleer", "desleyeren": "desleer",

    # ENTREVER
    "entrevea": "entrever", "entreveas": "entrever", "entrevea": "entrever", "entreveamos": "entrever", "entreveáis": "entrever", "entrevean": "entrever",
    "entreviera": "entrever", "entrevieras": "entrever", "entreviera": "entrever", "entreviéramos": "entrever", "entrevieras": "entrever", "entrevieran": "entrever",
    "entreviese": "entrever", "entrevieses": "entrever", "entreviese": "entrever", "entreviésemos": "entrever", "entrevieseis": "entrever", "entreviesen": "entrever",
    "entreviere": "entrever", "entrevieres": "entrever", "entreviere": "entrever", "entreviéremos": "entrever", "entreviereis": "entrever", "entrevieren": "entrever",

    # CUMPLIR
    "cumpla": "cumplir", "cumplas": "cumplir", "cumpla": "cumplir", "cumplamos": "cumplir", "cumpláis": "cumplir", "cumplan": "cumplir",
    "cumpliera": "cumplir", "cumplieras": "cumplir", "cumpliera": "cumplir", "cumpliéramos": "cumplir", "cumplieras": "cumplir", "cumplieran": "cumplir",
    "cumpliese": "cumplir", "cumplieses": "cumplir", "cumpliese": "cumplir", "cumpliésemos": "cumplir", "cumplieseis": "cumplir", "cumpliesen": "cumplir",
    "cumpliere": "cumplir", "cumplieres": "cumplir", "cumpliere": "cumplir", "cumpliéremos": "cumplir", "cumpliereis": "cumplir", "cumplieren": "cumplir",

    # SONREÍR
    "sonría": "sonreír", "sonrías": "sonreír", "sonría": "sonreír", "sonriamos": "sonreír", "sonriáis": "sonreír", "sonrían": "sonreír",
    "sonriera": "sonreír", "sonrieras": "sonreír", "sonriera": "sonreír", "sonriéramos": "sonreír", "sonrieras": "sonreír", "sonrieran": "sonreír",
    "sonriese": "sonreír", "sonrieses": "sonreír", "sonriese": "sonreír", "sonriésemos": "sonreír", "sonrieseis": "sonreír", "sonriesen": "sonreír",
    "sonriere": "sonreír", "sonrieres": "sonreír", "sonriere": "sonreír", "sonriéremos": "sonreír", "sonriereis": "sonreír", "sonrieren": "sonreír",

    # DESOÍR
    "desoiga": "desoír", "desoigas": "desoír", "desoiga": "desoír", "desoigamos": "desoír", "desoigáis": "desoír", "desoigan": "desoír",
    "desoyera": "desoír", "desoyeran": "desoír", "desoyera": "desoír", "desoyéramos": "desoír", "desoyeran": "desoír", "desoyeran": "desoír",
    "desoyese": "desoír", "desoyses": "desoír", "desoyese": "desoír", "desoyésemos": "desoír", "desoyeseis": "desoír", "desoysen": "desoír",
    "desoyere": "desoír", "desoyeres": "desoír", "desoyere": "desoír", "desoyéremos": "desoír", "desoyereis": "desoír", "desoyeren": "desoír",

    # PERCIBIR
    "perciba": "percibir", "percibas": "percibir", "perciba": "percibir", "percibamos": "percibir", "percibáis": "percibir", "perciban": "percibir",
    "percibiera": "percibir", "percibieras": "percibir", "percibiera": "percibir", "percibiéramos": "percibir", "percibieras": "percibir", "percibieran": "percibir",
    "percibiese": "percibir", "percibieses": "percibir", "percibiese": "percibir", "percibiésemos": "percibir", "percibieseis": "percibir", "percibiesen": "percibir",
    "percibiere": "percibir", "percibieres": "percibir", "percibiere": "percibir", "percibiéremos": "percibir", "percibiereis": "percibir", "percibieren": "percibir",

    # ELEGIR
    "elija": "elegir", "elijas": "elegir", "elija": "elegir", "elijamos": "elegir", "elijáis": "elegir", "elijan": "elegir",
    "eligiera": "elegir", "eligieras": "elegir", "eligiera": "elegir", "eligieran": "elegir", "eligiera": "elegir", "eligieran": "elegir",
    "eligiese": "elegir", "eligieses": "elegir", "eligiese": "elegir", "eligiese": "elegir", "eligieseis": "elegir", "eligiesen": "elegir",
    "eligiere": "elegir", "eligieres": "elegir", "eligiere": "elegir", "eligiéremos": "elegir", "eligiereis": "elegir", "eligieren": "elegir",

    # ESCOGER
    "escoja": "escoger", "escojas": "escoger", "escoja": "escoger", "escojamos": "escoger", "escojáis": "escoger", "escojan": "escoger",
    "escogiera": "escoger", "escogieras": "escoger", "escogiera": "escoger", "escogiéramos": "escoger", "escogieras": "escoger", "escogieran": "escoger",
    "escogiese": "escoger", "escogieses": "escoger", "escogiese": "escoger", "escogiésemos": "escoger", "escogieseis": "escoger", "escogiesen": "escoger",
    "escogiere": "escoger", "escogieres": "escoger", "escogiere": "escoger", "escogiéremos": "escoger", "escogiereis": "escoger", "escogieren": "escoger",
}

# Conjunto para búsquedas rápidas
SUBJ_SET = set(SUBJUNTIVO_COMPLETO.keys()

def detectar_subjuntivo(texto):
    palabras = re.findall(r'\b\w+\b', texto, re.IGNORECASE)
    encontrados = []
    vistos = set()
    for palabra in palabras:
        forma = palabra.lower()
        if forma in SUBJ_SET and forma not in vistos:
            lema = SUBJUNTIVO_COMPLETO[forma]
            # Tiempo
            if forma.endswith(("ra", "se", "ramos", "semos", "rais", "seis", "ran", "sen")):
                tiempo = "Imperfecto"
            elif forma.endswith("re"):
                tiempo = "Futuro"
            else:
                tiempo = "Presente"
            # Número
            numero = "Plural" if forma.endswith(("mos", "is", "n", "áis", "ais")) else "Singular"
            # Persona (aproximada)
            persona = {
                "o": "1ª", "as": "2ª", "a": "3ª", "amos": "1ª", "áis": "2ª", "is": "2ª", "n": "3ª"
            }.get(forma[-2:], "Desconocida") if len(forma) > 2 else "Desconocida"

            encontrados.append({
                "Verbo": palabra,
                "Lema": lema,
                "Tiempo": tiempo,
                "Modo": "Subjuntivo",
                "Persona": persona,
                "Número": numero
            })
            vistos.add(forma)
    return encontrados

# --- Interfaz ---
uploaded_file = st.file_uploader("📤 Sube tu archivo .txt", type=["txt"])

if uploaded_file is not None:
    try:
        texto = uploaded_file.read().decode("utf-8")
        st.success("✅ Archivo cargado.")

        with st.expander("📄 Ver texto"):
            st.text(texto)

        # Analizar
        verbos = detectar_subjuntivo(texto)

        if verbos:
            df = pd.DataFrame(verbos)
            st.subheader(f"🎉 Se encontraron {len(df)} verbos en subjuntivo")

            tab1, tab2, tab3 = st.tabs(["📊 Estadísticas", "📄 Texto resaltado", "📋 Detalles"])

            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    fig1 = px.pie(df, names="Tiempo", title="Tiempo verbal")
                    st.plotly_chart(fig1)
                with col2:
                    fig2 = px.pie(df, names="Lema", title="Verbos más usados")
                    st.plotly_chart(fig2)

            with tab2:
                highlighted = texto
                for v in sorted(df["Verbo"].unique(), key=len, reverse=True):
                    highlighted = re.sub(
                        rf'\b({re.escape(v)})\b',
                        f'<mark style="background: #FFEB3B; padding: 2px 6px; border-radius: 4px; font-weight: bold;">\\1</mark>',
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
                file_name="verbos_subjuntivo.csv",
                mime="text/csv"
            )
        else:
            st.info("ℹ️ No se encontraron verbos en subjuntivo.")

    except Exception as e:
        st.error("❌ Error al procesar el archivo.")
        st.exception(e)
else:
    st.info("👈 Sube un archivo .txt para comenzar.")
