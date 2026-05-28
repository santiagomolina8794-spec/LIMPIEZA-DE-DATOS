import streamlit as st
import pandas as pd

from ydata_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report

# ==========================================
# CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title="YData Profiling",
    layout="wide"
)

st.title("Análisis Automático de Datos")

st.write(
    "Carga un archivo y genera un reporte automático."
)

# ==========================================
# CARGAR ARCHIVO
# ==========================================

archivo = st.file_uploader(
    "Seleccione un archivo",
    type=["csv", "xlsx", "json"]
)

# ==========================================
# PROCESAR ARCHIVO
# ==========================================

if archivo is not None:

    try:

        nombre = archivo.name

        # ==========================================
        # LEER ARCHIVO
        # ==========================================

        if nombre.endswith(".csv"):

            df = pd.read_csv(archivo, delimiter=";")

        elif nombre.endswith(".xlsx"):

            df = pd.read_excel(archivo)

        elif nombre.endswith(".json"):

            df = pd.read_json(archivo)

        # ==========================================
        # MOSTRAR DATOS
        # ==========================================

        st.subheader("Vista de Datos")

        st.dataframe(df)

        # ==========================================
        # INFORMACIÓN GENERAL
        # ==========================================

        st.subheader("Información General")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Filas", df.shape[0])

        with col2:
            st.metric("Columnas", df.shape[1])

        with col3:
            st.metric(
                "Valores Nulos",
                df.isnull().sum().sum()
            )

        # ==========================================
        # GENERAR REPORTE
        # ==========================================

        st.subheader("Reporte Automático")

        profile = ProfileReport(
            df,
            title="Reporte de Datos",
            explorative=True
        )

        st_profile_report(profile)

    except Exception as e:

        st.error(f"Error: {e}")