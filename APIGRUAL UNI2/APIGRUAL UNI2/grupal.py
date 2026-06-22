import streamlit as st
import pandas as pd
import requests
import sqlite3
import matplotlib.pyplot as plt

st.set_page_config(page_title="Universidades del Ecuador", layout="wide")

st.title("Análisis de Universidades del Ecuador")
st.write("Consumo de API, SQLite, visualización y exportación a CSV")

# API real de universidades del Ecuador
url = "http://universities.hipolabs.com/search?country=Ecuador"

try:
    respuesta = requests.get(url)
    datos = respuesta.json()

    # Convertir a DataFrame
    df = pd.DataFrame(datos)

    # Seleccionar columnas importantes
    df = df[["name", "state-province", "domains"]]

    # Cambiar nombres de columnas
    df.columns = ["Universidad", "Provincia", "Dominio"]

    # Convertir listas a texto para SQLite
    df["Dominio"] = df["Dominio"].apply(
        lambda x: ", ".join(x) if isinstance(x, list) else str(x)
    )

    # Mostrar datos
    st.subheader("Datos obtenidos desde la API")
    st.dataframe(df)

    # Guardar en SQLite
    conexion = sqlite3.connect("universidades.db")

    df.to_sql(
        "universidades",
        conexion,
        if_exists="replace",
        index=False
    )

    conexion.close()

    st.success("Datos guardados correctamente en SQLite")

    # Mostrar datos desde SQLite
    st.subheader("Datos almacenados en SQLite")

    conexion = sqlite3.connect("universidades.db")

    consulta = pd.read_sql_query(
        "SELECT * FROM universidades",
        conexion
    )

    conexion.close()

    st.dataframe(consulta)

    # -----------------------------
    # Gráfico con sentido
    # -----------------------------
    st.subheader("Distribución de universidades públicas y privadas")

    # Clasificación simple
    universidades_publicas = [
        "Central",
        "Estatal",
        "Politécnica",
        "de Guayaquil",
        "de Cuenca",
        "de Loja",
        "de Milagro"
    ]

    df["Tipo"] = df["Universidad"].apply(
        lambda x: "Pública"
        if any(palabra in x for palabra in universidades_publicas)
        else "Privada"
    )

    conteo = df["Tipo"].value_counts()

    fig, ax = plt.subplots()

    conteo.plot(
        kind="pie",
        autopct="%1.1f%%",
        ax=ax
    )

    ax.set_ylabel("")
    ax.set_title("Universidades públicas vs privadas")

    st.pyplot(fig)

    # Exportar CSV
    st.subheader("Exportar datos")

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Descargar CSV",
        data=csv,
        file_name="universidades_ecuador.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"Error: {e}")