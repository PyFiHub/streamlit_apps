import streamlit as st
import pandas as pd
import sqlite3
import os
from streamlit_ace import st_ace

# Define Functions

# SQL
def get_data_with_columns(query, params=()):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trading_data.db")
    data = None
    column_names = None
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute(query, params)
            data = c.fetchall()
            column_names = [description[0] for description in c.description]
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
    return data, column_names

# SCHEMA
def get_schema(table_name):
    query = f"PRAGMA table_info({table_name})"
    data, _ = get_data_with_columns(query)
    return data

# MAIN

# NUMBER OF TABLE IN DATABASE
num_tables, _ = get_data_with_columns("SELECT count(name) FROM sqlite_master WHERE type='table'")
num_tables = num_tables[0][0]
# TABLE NAMES
tables, _ = get_data_with_columns("SELECT name FROM sqlite_master WHERE type='table'")
assets = [table[0].replace("pair_", "") for table in tables]
assets = sorted(assets)

# DEFAULT VALUE FOR STREAMLIT SELECTBOX
default_asset = 'BTCUSDT'
default_asset_index = assets.index(default_asset) if default_asset in assets else 0

# STREAMLIT MAIN
st.set_page_config(page_title="SQL Playground", layout="centered")
st.title('SQL Playground')

# ASSET SELECT BOX
selected_asset = st.selectbox("Select an asset", assets, index=default_asset_index)
selected_table = f"pair_{selected_asset}"

# QUERY TEMPLATE
sma_200 = f'''
SELECT close_time, close, volume, num_trades, 
AVG(close) OVER (ORDER BY close_time ROWS BETWEEN 199 PRECEDING AND CURRENT ROW) AS SMA_200
FROM {selected_table}
ORDER BY close_time DESC
LIMIT 200;
'''
rsi = f'''
WITH changes AS (
    SELECT
        close_time,
        close,
        close - LAG(close) OVER (ORDER BY close_time) AS price_change
    FROM {selected_table}
)
SELECT
    close_time,
    close,
    100 - (100 / (1 + (
        SUM(CASE WHEN price_change > 0 THEN price_change ELSE 0 END) OVER (ORDER BY close_time ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) /
        NULLIF(SUM(CASE WHEN price_change < 0 THEN ABS(price_change) ELSE 0 END) OVER (ORDER BY close_time ROWS BETWEEN 13 PRECEDING AND CURRENT ROW), 0)
    ))) AS rsi
FROM changes
ORDER BY close_time DESC
LIMIT 200;
'''

macd = f'''
WITH moving_averages AS (
    SELECT
        close_time,
        close,
        AVG(close) OVER (ORDER BY close_time ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) AS short_term_avg,
        AVG(close) OVER (ORDER BY close_time ROWS BETWEEN 25 PRECEDING AND CURRENT ROW) AS long_term_avg
    FROM {selected_table}
)
SELECT
    close_time,
    close,
    (short_term_avg - long_term_avg) AS macd,
    AVG(short_term_avg - long_term_avg) OVER (ORDER BY close_time ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS signal_line
FROM moving_averages
ORDER BY close_time DESC
LIMIT 200;
'''

query_templates = {
    "SMA 200": f"{sma_200}",
    "RSI": f"{rsi}",
    "MACD": f"{macd}",
}


selected_template = st.selectbox("Select a Query Template", list(query_templates.keys()))

# ST_ACE ENCHANTED EDITOR
sql_query = st_ace(value=query_templates[selected_template], language="sql", theme="xcode", font_size=14, height=350)

# CALL GET DATA
# Session State required to keep data in store and persist state - https://docs.streamlit.io/library/api-reference/session-state
if st.button('Submit'):
    st.session_state.data, st.session_state.column_names = get_data_with_columns(sql_query)

if 'data' in st.session_state and 'column_names' in st.session_state:
    df = pd.DataFrame(st.session_state.data, columns=st.session_state.column_names)
    st.write(f"Number of rows: {len(df)}")
    st.dataframe(df)
    # Add the Download CSV button
    csv = df.to_csv(index=False)
    st.download_button(label="Download CSV (UTF-8 encoding)", data=csv, file_name=f"{selected_asset}_price_data.csv", mime="text/csv")

# SIDEBAR SETTINGS
st.sidebar.title(f'Binance Historical Trading Data - SQL Practice')
st.sidebar.markdown(f'Number of Tables :```{num_tables}```')

st.sidebar.markdown(f'### Table Schema :```{selected_table}```')
st.sidebar.dataframe(pd.DataFrame(get_schema(selected_table), columns=["ID", "Column Name", "Data Type", "Not Null", "Default Value", "Primary Key"]).set_index("Column Name"))

# SIDEBAR EXPANDERS
with st.sidebar.expander("Other Streamlit Demos"):
    st.markdown("[GitHub PyFiHub](https://github.com/PyFiHub/streamlit_apps)")

with st.sidebar.expander("SQL Help & Tutorials"):
    st.markdown("[Learn SQL Basics (W3Schools)](https://www.w3schools.com/sql/)")

