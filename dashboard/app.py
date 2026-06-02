import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="USA Weather Trends", layout="wide")
st.title("USA Weather Trends (Past 1 Year)")
st.markdown("This dashboard queries **Apache Iceberg** directly using **DuckDB**.")

@st.cache_data
def load_data():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    iceberg_path = os.path.join(project_root, 'data', 'iceberg_warehouse', 'weather', 'historical')
    
    if not os.path.exists(iceberg_path):
        return pd.DataFrame()
        
    conn = duckdb.connect()
    
    try:
        # Load extensions for Iceberg
        conn.execute("INSTALL iceberg;")
        conn.execute("LOAD iceberg;")
        conn.execute("SET unsafe_enable_version_guessing = true;")
        
        # Query Iceberg directly and aggregate
        query = f"""
            WITH staging AS (
                SELECT * FROM iceberg_scan('{iceberg_path}')
            ),
            monthly_agg AS (
                SELECT
                    city AS city_name,
                    date_trunc('month', CAST(date AS DATE)) AS month,
                    avg(temp_max_c) AS avg_temp_max_c,
                    avg(temp_min_c) AS avg_temp_min_c,
                    sum(precipitation_mm) AS total_precipitation_mm,
                    max(wind_speed_max_kmh) AS max_wind_speed_kmh
                FROM staging
                WHERE city IS NOT NULL
                GROUP BY 1, 2
            )
            SELECT * FROM monthly_agg ORDER BY city_name, month
        """
        df = conn.execute(query).df()
    except Exception as e:
        st.error(f"Error querying DuckDB/Iceberg: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()
        
    return df

df = load_data()

if df.empty:
    st.warning("No data found! Please make sure you have run the Airflow pipeline (Extract -> Iceberg).")
else:
    cities = df['city_name'].unique().tolist()
    selected_cities = st.multiselect("Select Cities", cities, default=cities[:3])
    
    filtered_df = df[df['city_name'].isin(selected_cities)]
    
    st.subheader("Monthly Average Maximum Temperature (°C)")
    fig_temp = px.line(filtered_df, x='month', y='avg_temp_max_c', color='city_name', markers=True)
    st.plotly_chart(fig_temp, use_container_width=True)
    
    st.subheader("Monthly Total Precipitation (mm)")
    fig_precip = px.bar(filtered_df, x='month', y='total_precipitation_mm', color='city_name', barmode='group')
    st.plotly_chart(fig_precip, use_container_width=True)
    
    st.subheader("Raw Data Preview")
    st.dataframe(filtered_df.head(100))
