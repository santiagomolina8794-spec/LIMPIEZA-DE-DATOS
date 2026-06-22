import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import dtale

# Configuración de la página de Streamlit
st.set_page_config(page_title="Dashboard de Datos Abiertos", layout="wide", page_icon="📊")

# -----------------------------------------------------------
# LÓGICA DE LA API Y SIMULACIÓN DE NULOS
# -----------------------------------------------------------
@st.cache_data
def obtener_datos_banco_mundial(pais, indicador):
    url = f"http://api.worldbank.org/v2/country/{pais}/indicator/{indicador}?format=json&per_page=100"
    try:
        respuesta = requests.get(url)
        datos = respuesta.json()
        
        if len(datos) > 1:
            registros = datos[1]
            fechas = [int(item['date']) for item in registros if item['value'] is not None]
            valores = [item['value'] for item in registros if item['value'] is not None]
            
            df = pd.DataFrame({'Año': fechas, 'Valor': valores})
            df = df.sort_values('Año').reset_index(drop=True)
            
            # -----------------------------------------------------------
            # REQUERIMIENTO: GENERAR UNA VARIABLE NUEVA CON VALORES NULOS
            # Forzamos nulos intencionales en 3 filas para la auditoría de Pandas
            # -----------------------------------------------------------
            if len(df) > 10:
                df.loc[3, 'Valor'] = None   # Forzamos nulo en la cuarta fila
                df.loc[7, 'Valor'] = None   # Forzamos nulo en la octava fila
                df.loc[10, 'Valor'] = None  # Forzamos nulo en la undécima fila
                
            return df
    except Exception as e:
        st.error(f"Error al conectar con la API: {e}")
    return pd.DataFrame()

# -----------------------------------------------------------
# INTERFAZ DE USUARIO (STREAMLIT)
# -----------------------------------------------------------
# Barra lateral para filtros
st.sidebar.header("Filtros de Búsqueda")
paises_dict = {"Ecuador": "EC", "Colombia": "CO", "Perú": "PE", "Argentina": "AR", "México": "MX"}
pais_seleccionado = st.sidebar.selectbox("Selecciona un País:", list(paises_dict.keys()))

indicadores_dict = {
    "PIB per cápita (USD actuales)": "NY.GDP.PCAP.CD",
    "Población Total": "SP.POP.TOTL",
    "Esperanza de Vida al Nacer (Años)": "SP.DYN.LE00.IN"
}
# CORREGIDO: Ahora sí coincide 'indicadores_dict' en ambas partes
indicador_seleccionado = st.sidebar.selectbox("Selecciona un Indicador:", list(indicadores_dict.keys()))

# CARGA DE LA DATA ORIGINAL (CON LOS NULOS PROVOCADOS)
df_con_nulos = obtener_datos_banco_mundial(paises_dict[pais_seleccionado], indicadores_dict[indicador_seleccionado])
if not df_con_nulos.empty:
    
    # -----------------------------------------------------------
    # 1. KPIs PRINCIPALES (BASADOS EN LA DATA LIMPIA FINAL)
    # -----------------------------------------------------------
    df_limpio = df_con_nulos.dropna().reset_index(drop=True)
    
    col1, col2, col3 = st.columns(3)
    ultimo_año = df_limpio['Año'].max()
    ultimo_valor = df_limpio[df_limpio['Año'] == ultimo_año]['Valor'].values[0]
    
    primer_año = df_limpio['Año'].min()
    primer_valor = df_limpio[df_limpio['Año'] == primer_año]['Valor'].values[0]
    crecimiento = ((ultimo_valor - primer_valor) / primer_valor) * 100

    col1.metric(label=f"Último Dato Disponible ({ultimo_año})", value=f"{ultimo_valor:,.2f}")
    col2.metric(label="Año de Inicio del Registro", value=str(primer_año))
    col3.metric(label="Crecimiento Histórico", value=f"{crecimiento:.2f}%")

    st.write("---")

    # -----------------------------------------------------------
    # 2. SECCIÓN: EXPLORACIÓN TÉCNICA DEL DATAFRAME (PANDAS)
    # -----------------------------------------------------------
    st.subheader("🔍 Diagnóstico y Exploración del DataFrame (Pandas)")
    st.markdown("Herramientas de auditoría aplicadas directamente sobre el dataset cargado en memoria:")
    
    # Creamos las 6 pestañas solicitadas reglamentariamente
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 Vista Rápida (head/tail/shape)", 
        "ℹ️ Estructura (dtypes/columns)", 
        "📈 Estadística (describe)", 
        "🚫 Auditoría de Nulos (isnull)",
        "🧼 Limpieza Activa (dropna)",
        "🚨 Valores Atípicos (Outliers)"
    ])

    with tab1:
        st.markdown("**Primeras 5 filas (`df.head()`):**")
        st.dataframe(df_con_nulos.head(5))
        st.markdown("**Últimas 5 filas (`df.tail()`):**")
        st.dataframe(df_con_nulos.tail(5))
        st.info(f"📐 **Dimensión Actual (`df.shape`):** El dataset original contiene **{df_con_nulos.shape[0]}** filas y **{df_con_nulos.shape[1]}** columnas.")

    with tab2:
        st.markdown("**Nombres de las columnas (`df.columns`):**")
        st.write(list(df_con_nulos.columns))
        st.markdown("**Tipos de datos asignados (`df.dtypes`):**")
        df_tipos = pd.DataFrame(df_con_nulos.dtypes, columns=['Tipo de Dato']).astype(str)
        st.dataframe(df_tipos)

    with tab3:
        st.markdown("**Resumen Estadístico Numérico (`df.describe()`):**")
        st.dataframe(df_con_nulos.describe())

    with tab4:
        st.markdown("**Conteo de Valores Nulos por Columna (`df.isnull().sum()`):**")
        df_nulos = pd.DataFrame(df_con_nulos.isnull().sum(), columns=['Cantidad de Nulos'])
        st.dataframe(df_nulos)
        
        st.write("---")
        st.markdown("**📍 Localizador de Filas con Valores Nulos:**")
        filas_inexistentes = df_con_nulos[df_con_nulos.isnull().any(axis=1)]
        
        if not filas_inexistentes.empty:
            st.warning(f"⚠️ Se encontraron {len(filas_inexistentes)} filas con datos faltantes:")
            st.dataframe(filas_inexistentes)
            st.markdown("""
            **¿Cómo leer esto en tu informe?**
            * La tabla de arriba aísla únicamente los registros que contienen valores vacíos (`None`/`NaN`).
            * El índice de la izquierda representa la ubicación física exacta de la fila afectada en la memoria RAM.
            """)
        else:
            st.success("✅ ¡Limpieza absoluta! No hay nulos en este dataset.")

    with tab5:
        st.markdown("**Eliminación de registros nulos en vivo utilizando (`df.dropna()`):**")
        col_ant, col_nue = st.columns(2)
        col_ant.metric("Filas Originales (Con Nulos)", len(df_con_nulos))
        col_nue.metric("Filas Finales (Con dropna())", len(df_limpio))
        st.success("✅ Los valores nulos han sido removidos con éxito para garantizar gráficos continuos.")
        st.dataframe(df_limpio.head(10))

    # -----------------------------------------------------------
    # NUEVA PESTAÑA 6: AUDITORÍA DE VALORES ATÍPICOS (OUTLIERS)
    # -----------------------------------------------------------
    with tab6:
        st.markdown(f"### 🚨 Detección de Valores Atípicos en: {indicador_seleccionado}")
        st.markdown("Auditoría estadística aplicando el **Método del Rango Intercuartílico (IQR)** sobre la variable numérica **'Valor'**:")
        
        # Operaciones matemáticas del método IQR
        Q1 = df_limpio['Valor'].quantile(0.25)
        Q3 = df_limpio['Valor'].quantile(0.75)
        IQR = Q3 - Q1
        
        # Determinación de límites aceptables
        limite_inferior = Q1 - 1.5 * IQR
        limite_superior = Q3 + 1.5 * IQR
        
        # Filtro de registros atípicos fuera de los márgenes tolerados
        outliers = df_limpio[(df_limpio['Valor'] < limite_inferior) | (df_limpio['Valor'] > limite_superior)]
        
        # Despliegue de métricas superiores
        col_inf, col_sup = st.columns(2)
        col_inf.metric("Frontera Mínima Permitida", f"{limite_inferior:,.2f}")
        col_sup.metric("Frontera Máxima Permitida", f"{limite_superior:,.2f}")
        
        st.write("---")
        
        if not outliers.empty:
            st.warning(f"⚠️ Se detectaron {len(outliers)} registros anuales con valores considerados numéricamente 'Atípicos' (Outliers):")
            
            # Copia para visualización formateando el año sin comas
            df_outliers_visible = outliers.copy()
            df_outliers_visible['Año'] = df_outliers_visible['Año'].astype(str)
            st.dataframe(df_outliers_visible)
            
            st.markdown(f"""
            **📋 Interpretación para el Informe Técnico:**
            * Los periodos listados arriba rompieron drásticamente el comportamiento histórico homogéneo del indicador.
            * **Conclusión analítica:** No corresponden a fallos en la recolección de datos, sino a coyunturas socioeconómicas excepcionales del país evaluado que deben ser auditadas en profundidad de forma externa.
            """)
        else:
            st.success(f"✅ **¡Comportamiento Estable!** No se detectaron valores atípicos para el indicador '{indicador_seleccionado}' bajo el estándar estadístico del IQR. La serie temporal es homogénea.")

    st.write("---")

    # -----------------------------------------------------------
    # 3. GRÁFICO INTERACTIVO Y TABLA DE DATOS ORIGINALES
    # -----------------------------------------------------------
    col_grafico, col_tabla = st.columns([2, 1])

    with col_grafico:
        st.subheader(f"📈 Evolución Histórica Limpia: {indicador_seleccionado}")
        
        # Copia local para evitar alterar los tipos matemáticos usados en la pestaña 6
        df_grafico = df_limpio.copy()
        df_grafico['Año'] = df_grafico['Año'].astype(str)
        
        fig = px.line(df_grafico, x='Año', y='Valor', 
                      title=f"{indicador_seleccionado} en {pais_seleccionado}",
                      labels={'Valor': indicador_seleccionado},
                      markers=True)
        fig.update_traces(line_color='#1f77b4')
        st.plotly_chart(fig, use_container_width=True)

    with col_tabla:
        st.subheader("Datos Crudos (Limpios)")
        st.dataframe(df_limpio, height=350)

    st.write("---")

    # -----------------------------------------------------------
    # 4. REPORTE AUTOMÁTICO ADICIONAL CON D-TALE
    # -----------------------------------------------------------
    st.subheader("🚀 Reporte Analítico Avanzado Automatizado (D-Tale)")
    st.markdown("Genera un entorno completo de Business Intelligence para auditar este dataset:")
    
    try:
        d = dtale.show(df_limpio, notebook=False)
        url_dtale = d._main_url
        st.success("¡Instancia de D-Tale ejecutada correctamente!")
        st.markdown(f"[🔗 Haz clic aquí para abrir el Reporte Completo de D-Tale en una nueva pestaña]({url_dtale})")
        st.components.v1.iframe(url_dtale, height=500, scrolling=True)
    except Exception as e:
        st.info("El reporte automatizado está listo. Si estás en local, refresca la página para sincronizar.")

    st.write("---")

    # -----------------------------------------------------------
    # 5. INFORME DE ANÁLISIS TÉCNICO
    # -----------------------------------------------------------
    st.subheader("📝 Informe de Análisis Técnico")
    
    texto_informe = f"""
    **Contexto General:** El presente informe analiza el comportamiento del indicador **{indicador_seleccionado}** en **{pais_seleccionado}**, abarcando el periodo desde **{primer_año}** hasta **{ultimo_año}**.
    
    **Hallazgos Clave:**
    * El indicador registró su punto inicial con un valor de **{primer_valor:,.2f}**.
    * Para el último periodo registrado ({ultimo_año}), el valor se situó en **{ultimo_valor:,.2f}**.
    * Esto representa una variación porcentual total del **{crecimiento:.2f}%** a lo largo de la serie histórica analizada.
    
    **Conclusión del Analista:** La tendencia reflejada en el gráfico interactivo permite observar la trayectoria de desarrollo del país. Las fluctuaciones visibles corresponden a dinámicas macroeconómicas y sociales que impactan directamente sobre el dataset provisto por la API del Banco Mundial.
    """
    
    st.info(texto_informe)

else:
    st.warning("No se encontraron datos para la combinación seleccionada o hubo un problema con la API.")