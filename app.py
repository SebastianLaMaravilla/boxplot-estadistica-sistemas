import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ---------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------
st.set_page_config(page_title="Medidas de Posición y Box-Plot", layout="wide", page_icon="📊")

st.title("📊 Análisis de Medidas de Posición y Detección de Anomalías")
st.markdown("**Ingeniería de Sistemas** | Creado por: Tatiana Andrea Ortega y Sebastian Perez")
st.markdown("---")

# ---------------------------------------------------------
# 1. CARGUE DE DATOS Y SIMULACIÓN DE CASOS
# ---------------------------------------------------------
st.sidebar.header("📂 Cargue de Datos")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo CSV o Excel", type=["csv", "xlsx"])

caso_estudio = st.sidebar.selectbox(
    "O selecciona un caso práctico de la presentación:",
    ("Caso 1: Latencia en Microservicios", "Caso 2: Ejecución en BD SQL")
)

@st.cache_data
def generar_datos_caso(caso):
    np.random.seed(42)
    if caso == "Caso 1: Latencia en Microservicios":
        datos_base = np.random.normal(loc=145, scale=40, size=200)
        datos_base = np.clip(datos_base, 80, 220) 
        outliers = np.array([450, 620])
        return pd.DataFrame({"Latencia_ms": np.concatenate([datos_base, outliers])})
    else:
        datos_base = np.random.normal(loc=0.4, scale=0.15, size=200)
        outliers = np.random.uniform(8.5, 12.0, size=16)
        return pd.DataFrame({"Tiempo_Ejecucion_s": np.concatenate([datos_base, outliers])})

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.sidebar.success("Archivo cargado correctamente.")
    except Exception as e:
        st.sidebar.error(f"Error al leer el archivo: {e}")
        df = generar_datos_caso(caso_estudio)
else:
    st.sidebar.info(f"Usando datos simulados para: {caso_estudio}")
    df = generar_datos_caso(caso_estudio)

columnas_num = df.select_dtypes(include=[np.number]).columns.tolist()
columna_objetivo = st.sidebar.selectbox("Selecciona la métrica a analizar:", columnas_num)
datos = df[columna_objetivo].dropna()

# ---------------------------------------------------------
# 2. CÁLCULO DE MEDIDAS DE TENDENCIA CENTRAL Y DISPERSIÓN
# ---------------------------------------------------------
media = np.mean(datos)
mediana = np.median(datos)
desviacion = np.std(datos, ddof=1)
varianza = np.var(datos, ddof=1)

# ---------------------------------------------------------
# 3. CÁLCULO DINÁMICO DE MEDIDAS DE POSICIÓN Y LÍMITES
# ---------------------------------------------------------
q1 = np.percentile(datos, 25)
q3 = np.percentile(datos, 75)
iqr = q3 - q1

limite_inferior = q1 - 1.5 * iqr
limite_superior = q3 + 1.5 * iqr

outliers_df = datos[(datos < limite_inferior) | (datos > limite_superior)]

st.subheader(f"Resultados Analíticos para: `{columna_objetivo}`")

col1, col2, col3, col4 = st.columns(4)
col1.metric("📌 Promedio (Media)", f"{media:.2f}")
col2.metric("📌 Mediana (Q2)", f"{mediana:.2f}")
col3.metric("📈 Desviación Estándar", f"{desviacion:.2f}")
col4.metric("🚨 Outliers Detectados", f"{len(outliers_df)}")

st.markdown("#### Medidas de Posición (Cuartiles y Regla de Tukey)")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Q1 (25%)", f"{q1:.2f}")
c2.metric("Q3 (75%)", f"{q3:.2f}")
c3.metric("Rango Intercuartílico (IQR)", f"{iqr:.2f}")
c4.metric("Límite Inferior", f"{limite_inferior:.2f}")
c5.metric("Límite Superior", f"{limite_superior:.2f}")

# ---------------------------------------------------------
# 4. VISUALIZACIÓN GRÁFICA INTERACTIVA DEL BOX-PLOT
# ---------------------------------------------------------
st.markdown("---")
st.subheader("Visualización Gráfica Interactiva: Diagrama de Cajas y Alambres")

fig = go.Figure()

fig.add_trace(go.Box(
    y=datos,
    name=columna_objetivo,
    boxpoints='outliers',
    jitter=0.3,
    pointpos=0,
    marker=dict(color='rgb(187, 26, 83)'),
    line=dict(color='rgb(51, 60, 131)')
))

fig.add_shape(
    type="line", x0=-0.4, x1=0.4, y0=media, y1=media,
    line=dict(color="Green", width=2, dash="dashdot")
)
fig.add_annotation(x=0.45, y=media, text=f"Promedio: {media:.2f}", showarrow=False, font=dict(color="Green"))

fig.add_annotation(x=0.45, y=mediana, text=f"Mediana: {mediana:.2f}", showarrow=False, font=dict(color="Blue"))

fig.add_shape(type="line", x0=-0.4, x1=0.4, y0=limite_superior, y1=limite_superior, line=dict(color="Red", width=1, dash="dot"))
fig.add_annotation(x=-0.45, y=limite_superior, text=f"Límite Sup: {limite_superior:.2f}", showarrow=False, font=dict(color="Red"))

fig.add_shape(type="line", x0=-0.4, x1=0.4, y0=limite_inferior, y1=limite_inferior, line=dict(color="Red", width=1, dash="dot"))
fig.add_annotation(x=-0.45, y=limite_inferior, text=f"Límite Inf: {limite_inferior:.2f}", showarrow=False, font=dict(color="Red"))

fig.update_layout(
    title_text="Box-Plot de Anomalías en Infraestructura",
    yaxis_title=columna_objetivo,
    height=600,
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# EXTRAS: CÁLCULO DINÁMICO DE PERCENTILES
# ---------------------------------------------------------
st.markdown("---")
st.subheader("Calculadora Dinámica de Percentiles")
st.write("Mueve el deslizador para calcular cualquier percentil específico, útil para evaluar SLAs (ej. Percentil 90 o 95).")

percentil_deseado = st.slider("Selecciona el Percentil (P_k):", min_value=1, max_value=99, value=95, step=1)
valor_percentil = np.percentile(datos, percentil_deseado)

st.success(f"El valor para el **Percentil {percentil_deseado} (P_{percentil_deseado})** es: **{valor_percentil:.2f}**")
