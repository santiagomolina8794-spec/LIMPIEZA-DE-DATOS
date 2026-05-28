import streamlit as st
import pandas as pd
import dtale

st.set_page_config(
    page_title="Exploración de Datos con D-Tale",
    layout="wide"
)

st.title("Exploración Automática de Datos")

archivo = st.file_uploader(
    "Suba un archivo",
    type=["csv", "xlsx"]
)

if archivo is not None:

    # Leer archivo
    if archivo.name.endswith(".csv"):
        df = pd.read_csv(archivo, delimiter=";")

    else:
        df = pd.read_excel(archivo)

    # Mostrar datos
    st.subheader("Vista previa")
    st.dataframe(df)

    # Información básica
    st.subheader("Información del dataset")

    col1, col2, col3 = st.columns(3)

    col1.metric("Filas", df.shape[0])
    col2.metric("Columnas", df.shape[1])
    col3.metric("Valores nulos", df.isnull().sum().sum())

    # Tipos de datos
    st.subheader("Tipos de datos")
    st.write(df.dtypes)

    # Abrir D-Tale
    st.subheader("Exploración interactiva")

    d = dtale.show(df)

    st.markdown(
        f"""
        ### Abrir D-Tale
        
        [Click aquí para abrir D-Tale]({d._main_url})
        """,
        unsafe_allow_html=True
    )