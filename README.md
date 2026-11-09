# 📊 Monitor de Inflación Argentina (INDEC + Databricks)

Este proyecto implementa un pipeline de datos end-to-end que consume datos oficiales de series de tiempo del **INDEC** (a través de la API pública de `datos.gob.ar`), los procesa en **Databricks** utilizando la Arquitectura Medallion (Bronze, Silver, Gold) y los visualiza en un dashboard interactivo con **Streamlit**.

🔗 **[Ver Dashboard en Vivo](https://TU-URL-DE-STREAMLIT.streamlit.app/)** _(Reemplazá este link por el de tu app)_

---

## 🏗️ Arquitectura del Proyecto

El pipeline sigue la Arquitectura Medallion, garantizando la calidad y trazabilidad de los datos macroeconómicos:

1. **🥉 Capa Bronze (Ingesta):** Script en Python/PySpark que consulta la API de series de tiempo y guarda la respuesta JSON cruda en Delta Lake. Se añade un `ingestion_timestamp` para mantener un histórico de las extracciones.
2. **🥈 Capa Silver (Parseo y Limpieza):** Utiliza SQL puro en Databricks. Emplea funciones nativas de Spark como `from_json` y `explode` para desarmar el arreglo de datos anidado en el JSON y convertirlo en filas con columnas tipadas (`fecha` como DATE y `valor` como DOUBLE).
3. **🥇 Capa Gold (Analítica):** Utiliza SQL analítico avanzado. Mediante la función de ventana `LAG()`, calcula las variaciones porcentuales **mensuales** e **interanuales** del Índice de Precios al Consumidor (IPC).

## 📈 Características del Dashboard (Streamlit)

El dashboard conecta en tiempo real a Databricks para consumir la tabla Gold y presenta:

- **KPIs Principales:** Último mes disponible, inflación mensual e inflación interanual.
- **Gráfico de Barras (Variación Mensual):** Evolución de los últimos 36 meses con una escala de colores que resalta los picos inflacionarios.
- **Gráfico de Líneas (Variación Interanual):** Serie histórica para analizar la tendencia macroeconómica en el largo plazo.

## 🛠️ Tecnologías Utilizadas

- **Ingesta:** Python (`requests`, PySpark).
- **Procesamiento y Almacenamiento:** Databricks, Spark SQL, Delta Lake.
- **Visualización:** Streamlit (Community Cloud), Plotly, Pandas.
- **Fuente de Datos:** [API de Series de Tiempo de datos.gob.ar](https://apis.datos.gob.ar/series/api/series/)
- **Control de versiones:** Git / GitHub.

## ⚙️ Características Técnicas Destacadas

- **Procesamiento de JSON anidado:** La capa Silver demuestra cómo manipular respuestas JSON complejas de APIs reales y convertirlas en tablas relacionales eficientes.
- **Análisis de series de tiempo con SQL:** Uso de `LAG(valor, 1)` y `LAG(valor, 12)` para comparar períodos sin necesidad de usar Python.
- **Manejo de conexiones en Streamlit:** Implementación de reintentos automáticos y TTL (Time-To-Live) en el conector de Databricks para evitar caídas por inactividad del SQL Warehouse.
- **Seguridad:** Las credenciales de Databricks se manejan a través de secretos en Streamlit, nunca expuestas en el código.

## 📂 Estructura del Repositorio

```text
indec-inflation-dashboard/
│
├── dashboard/
│   ├── app.py                 # Código de la app de Streamlit
│   └── requirements.txt       # Dependencias
│
├── notebooks/
│   ├── 01_ingesta_bronze.py   # Notebook de Databricks (Python)
│   ├── 02_limpieza_silver.sql # Notebook de Databricks (SQL)
│   └── 03_gold_inflacion.sql  # Notebook de Databricks (SQL)
│
└── README.md                  # Este archivo
```
