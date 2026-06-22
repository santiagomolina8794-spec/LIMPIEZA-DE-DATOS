import streamlit as st
import pandas as pd
import pygwalker as pyg
from pygwalker.api.streamlit import StreamlitRenderer

st.title("Análisis con PyGWalker")

archivo = st.file_uploader("Suba un archivo", type=["csv", "xlsx"])

if archivo is not None:
    if archivo.name.endswith(".csv"):
        df = pd.read_csv(archivo, sep=";")
    else:
        df = pd.read_excel(archivo)
    
    st.dataframe(df)
    renderer = StreamlitRenderer(df)
    renderer.explorer()