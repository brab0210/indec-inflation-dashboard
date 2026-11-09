import streamlit as st
import pandas as pd
import plotly.express as px
from databricks import sql

st.set_page_config(page_title="INDEC Inflación", page_icon="📊", layout="wide")

st.title("📊 Monitor de Inflación (INDEC)")
st.markdown("Evolución del IPC y el poder adquisitivo basado en datos oficiales.")

# --- Configuración de la conexión ---
def get_databricks_connection():
    return sql.connect(
        server_hostname=st.secrets["DATABRICKS_HOST"],
        http_path=st.secrets["DATABRICKS_HTTP_PATH"],
        access_token=st.secrets["DATABRICKS_TOKEN"]
    )

@st.cache_resource(ttl=300)
def get_cached_connection():
    return get_databricks_connection()

@st.cache_data(ttl=600)
def load_data(query):
    try:
        conn = get_cached_connection()
        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return pd.DataFrame(result, columns=columns)
    except Exception:
        st.cache_resource.clear()
        conn = get_cached_connection()
        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return pd.DataFrame(result, columns=columns)

# --- ATENCIÓN ACÁ: Tu catálogo y esquema ---
CATALOG = "workspace"
SCHEMA = "indec_dataset_raw" # Cambiá esto si usaste otro nombre

# --- Consultas SQL ---
# Traemos todos los datos ordenados por fecha
query_datos = f"""
    SELECT * 
    FROM {CATALOG}.{SCHEMA}.gold_inflacion_calculada
    ORDER BY fecha ASC
"""

# --- Carga de datos ---
try:
    with st.spinner("Cargando datos del INDEC..."):
        df = load_data(query_datos)
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        # Separamos las series por si querés graficarlas juntas o por separado
        df_ipc = df[df['serie_id'] == '103.1_I2N_2016_M_15']
except Exception as e:
    st.error(f"Error al cargar los datos: {e}")
    st.stop()

# --- KPIs Principales (Último mes disponible) ---
ultimo_mes = df_ipc.iloc[-1] # Agarra la última fila

col1, col2, col3 = st.columns(3)
with col1:
    st.info(f"**Último Mes Disponible**\n\n### {ultimo_mes['fecha'].strftime('%B %Y')}")
with col2:
    st.info(f"**Inflación Mensual**\n\n### {ultimo_mes['variacion_mensual_pct']}%")
with col3:
    st.info(f"**Inflación Interanual**\n\n### {ultimo_mes['variacion_interanual_pct']}%")

st.divider()

# --- Gráfico 1: Evolución Mensual ---
st.subheader("📈 Evolución de la Inflación Mensual")
# Filtramos los últimos 36 meses para que el gráfico no se sature
df_mensual = df_ipc.tail(36) 

fig_mensual = px.bar(
    df_mensual, 
    x="fecha", 
    y="variacion_mensual_pct",
    title="Variación porcentual mes a mes",
    labels={"fecha": "Fecha", "variacion_mensual_pct": "Variación (%)"},
    color="variacion_mensual_pct",
    color_continuous_scale="Reds"
)
st.plotly_chart(fig_mensual, use_container_width=True)

# --- Gráfico 2: Evolución Interanual ---
st.subheader("📉 Evolución de la Inflación Interanual")
fig_interanual = px.line(
    df_ipc, 
    x="fecha", 
    y="variacion_interanual_pct",
    markers=True,
    title="Variación porcentual contra el mismo mes del año anterior",
    labels={"fecha": "Fecha", "variacion_interanual_pct": "Variación (%)"},
    color_discrete_sequence=["#1f77b4"]
)
st.plotly_chart(fig_interanual, use_container_width=True)