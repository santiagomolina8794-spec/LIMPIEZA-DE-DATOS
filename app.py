import streamlit as st
import pandas as pd
import pygwalker as pyg

st.set_page_config(
    page_title="Visualización Automática",
    layout="wide"
)

st.title("Lectura y Visualización Automática de Datos")

archivo = st.file_uploader(
    "Seleccione un archivo",
    type=["csv", "xlsx", "json", "txt"]
)

if archivo is not None:

    nombre = archivo.name

    # =========================
    # Lectura de archivos
    # =========================

    if nombre.endswith(".csv"):
        df = pd.read_csv(archivo)

    elif nombre.endswith(".xlsx"):
        df = pd.read_excel(archivo)

    elif nombre.endswith(".json"):
        df = pd.read_json(archivo)

    elif nombre.endswith(".txt"):
        df = pd.read_csv(archivo, sep=None, engine="python")

    # =========================
    # Mostrar datos
    # =========================

    st.subheader("Vista de Datos")

    st.dataframe(df)

    # =========================
    # Métricas
    # =========================

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Filas", df.shape[0])

    with col2:
        st.metric("Columnas", df.shape[1])

    with col3:
        st.metric("Nulos", df.isnull().sum().sum())

    # =========================
    # Visualización automática
    # =========================

    st.subheader("Exploración Visual Automática")

    html = pyg.to_html(df)

    st.components.v1.html(
        html,
        height=1000,
        scrolling=True
    )