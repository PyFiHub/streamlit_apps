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
st.title('SQL Playground')

# ASSET SELECT BOX
selected_asset = st.selectbox("Select an asset", assets, index=default_asset_index)
selected_table = f"pair_{selected_asset}"

# QUERY TEMPLATE
query_template = f'''
SELECT close_time, close, AVG(close) OVER (ORDER BY close_time ROWS BETWEEN 199 PRECEDING AND CURRENT ROW) AS SMA_200
FROM {selected_table}
ORDER BY close_time DESC
LIMIT 200;
'''
query_templates = {
    "Test Template": f"{query_template}",
}
selected_template = st.selectbox("Select a Query Template", list(query_templates.keys()))

#ST_ACE ENCHANTED EDITOR
sql_query = st_ace(value=query_templates[selected_template], language="sql", theme="xcode", font_size=14, height=200)

#CALL GET DATA
if st.button('Submit'):
    data, column_names = get_data_with_columns(sql_query)
    df = pd.DataFrame(data, columns=column_names)
    st.write(f"Number of rows: {len(df)}")
    st.dataframe(df)

# SIDEBAR SETTINGS
st.sidebar.title(f'Binance Historical Trading Data - SQL Practice')
st.sidebar.markdown(f'Number of Tables :```{num_tables}```')

st.sidebar.markdown("### Table Schema")
st.sidebar.dataframe(pd.DataFrame(get_schema(selected_table), columns=["ID", "Column Name", "Data Type", "Not Null", "Default Value", "Primary Key"]))

# SIDEBAR EXPANDERS
with st.sidebar.expander("Other Streamlit Demos"):
    st.markdown("[GitHub PyFiHub](https://github.com/PyFiHub/streamlit_apps)")

with st.sidebar.expander("SQL Help & Tutorials"):
    st.markdown("[Learn SQL Basics (W3Schools)](https://www.w3schools.com/sql/)")

