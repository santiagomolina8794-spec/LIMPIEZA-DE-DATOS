import json
import sqlite3

import requests
import pandas as pd
import streamlit as st

# Importamos d-tale y su componente para Streamlit
import dtale
import dtale.app as dtale_app

# Configuración de Streamlit
st.set_page_config(layout="wide")
st.title("De la API a SQLite, CSV y D-Tale")

# --- 1. OBTENCIÓN Y LIMPIEZA DE DATOS ---

respuesta = requests.get("https://jsonplaceholder.typicode.com/users")
datos_json = respuesta.json()
df_original = pd.DataFrame(datos_json)

# Convertimos las dos columnas que querías a texto
df_original['id'] = df_original['id'].astype(str)
df_original['name'] = df_original['name'].astype(str)

# Convertimos diccionarios/listas complejas a texto plano (JSON) para SQLite y CSV
for col in df_original.columns:
    if df_original[col].apply(lambda x: isinstance(x, (dict, list))).any():
        df_original[col] = df_original[col].apply(json.dumps)


# --- 2. GUARDAR EN SQLITE3 ---

conexion = sqlite3.connect("usuarios.db")
df_original.to_sql("tabla_usuarios", conexion, if_exists="replace", index=False)
conexion.close()


# --- 3. EXPORTAR A CSV (NUEVA LÍNEA) ---

# Guarda el DataFrame en un archivo llamado 'usuarios_exportados.csv'
# 'index=False' evita que se guarde una columna extra con los números de fila
df_original.to_csv("usuarios_exportados.csv", index=False, encoding="utf-8")

# Mensaje de éxito en Streamlit
st.success("¡Datos guardados con éxito en la base de datos 'usuarios.db' y exportados a 'usuarios_exportados.csv'!")


# --- 4. VISOR DE BASE DE DATOS EN LÍNEA (SQLITE) ---

st.header("🔍 Visor de la Base de Datos en Vivo")

tab1, tab2 = st.tabs(["📋 Ver Tabla Completa", "💻 Ejecutar Consulta SQL"])

with tab1:
    st.subheader("Contenido actual de 'tabla_usuarios'")
    conn = sqlite3.connect("usuarios.db")
    df_visor = pd.read_sql("SELECT * FROM tabla_usuarios", conn)
    conn.close()
    st.dataframe(df_visor, use_container_width=True)

with tab2:
    st.subheader("Escribe tu consulta SQL personalizada")
    consulta = st.text_input("Consulta:", value="SELECT id, name, email FROM tabla_usuarios")
    
    if st.button("Ejecutar Query"):
        try:
            conn = sqlite3.connect("usuarios.db")
            df_query = pd.read_sql(consulta, conn)
            conn.close()
            st.dataframe(df_query, use_container_width=True)
        except Exception as e:
            st.error(f"Error en la consulta: {e}")


# --- 5. INTEGRACIÓN DE D-TALE (ANALISIS AVANZADO) ---

st.header("📊 Análisis Avanzado con D-Tale")
dtale_app.JUPYTER_SERVER_PROXY = True

d = dtale.show(df_visor, open_browser=False)
st.components.v1.iframe(f"{d.main_url}", height=600, scrolling=True)

# ==========================================
# EXPORTAR A CSV, EXCEL Y JSON DESDE STREAMLIT
# ==========================================
if st.button("Exportar a CSV, Excel y JSON"):
    try:
        archivo = "usuarios_exportados.csv"
        nombre = archivo.lower()

        # Cargamos los datos actuales para poder exportarlos
        conexion_exportar = sqlite3.connect("usuarios.db")
        df_a_exportar = pd.read_sql("SELECT * FROM tabla_usuarios", conexion_exportar)
        conexion_exportar.close()

        # Condicionales tabulados correctamente:
        if nombre.endswith(".csv"):
            # Generamos los tres archivos locales en tu carpeta
            df_a_exportar.to_csv("usuarios_final.csv", index=False, encoding="utf-8")
            df_a_exportar.to_json("usuarios_final.json", orient="records", indent=4)
            
            # Nota: Para exportar a Excel (.xlsx) necesitas la librería openpyxl. 
            # Si te da error aquí, instala en tu terminal: pip install openpyxl
            df_a_exportar.to_excel("usuarios_final.xlsx", index=False)

            st.success("¡Archivos exportados con éxito en la carpeta de tu proyecto! (CSV, JSON y Excel)")
            
    except Exception as e:
        st.error(f"Error al exportar los archivos: {e}")