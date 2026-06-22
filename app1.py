import streamlit as st
import pandas as pd
import sweetviz as sv

st.title("Análisis Automático de Datos")

archivo = st.file_uploader(
    "Suba un archivo",
    type=["csv", "xlsx"]
)

if archivo is not None:

    if archivo.name.endswith(".csv"):
        df = pd.read_csv(archivo, sep=';')

    else:
        df = pd.read_excel(archivo)

    st.dataframe(df)

    reporte = sv.analyze(df)

    reporte.show_html(
        "reporte.html",
        open_browser=False
    )

    with open("reporte.html", "r", encoding="utf-8") as f:
        html = f.read()

    st.components.v1.html(
        html,
        width=1000,
        height=1000,
        scrolling=True
    )
    