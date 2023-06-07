"""
Cryptocurrency Live Prices Streamlit App
Description: Displays live prices of cryptocurrencies using the CoinGecko API - Streamlit Project.
Date: 2023-06-07
Version: 1.1
Author: PyFiHub
"""

import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

import base64
import io
import matplotlib.pyplot as plt

# API URL and parameters
COINGECKO_LOGO_URL = "https://static.coingecko.com/s/coingecko-branding-guide-8447de673439420efa0ab1e0e03a1f8b0137270fbc9c0b7c086ee284bd417fa1.png"
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/markets"
PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 100,
    "page": 1,
    "sparkline": "true",
    "price_change_percentage": "1h,24h,7d,30d,1y",
    "locale": "en",
}

def plot_sparkline(data, percentage_change_7d):
    fig, ax = plt.subplots(figsize=(2.2, 0.5), dpi=64)
    percentage_change_7d = float(percentage_change_7d)
    # Determine line color based on 7 days percentage change
    if percentage_change_7d > 0:
        line_color = 'green'
    elif percentage_change_7d < 0:
        line_color = 'red'
    else:
        line_color = 'gray'
    
    plt.plot(data, lw=1, color=line_color)
    ax.fill_between(range(len(data)), data, color=line_color, alpha=0.2)
    
    min_value = min(data)
    max_value = max(data)
    ax.set_ylim(min_value, max_value)
    
    plt.axis('off')
    plt.tight_layout()
    
    fig.patch.set_alpha(0)  # Set the background of the plot to be transparent
    ax.set_facecolor("none")  # Set the background of the axes to be transparent

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=64, transparent=True)  # Set transparent=True while saving the figure
    buf.seek(0)
    encoded_img = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return encoded_img

def fetch_data(url, params):
    # Fetch data from the API
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as e:
        st.error(f"An error occurred while fetching data: {e}")
        return None


st.set_page_config(page_title='Cryptocurrencies Live Prices (USD)- PyFiHub', layout='wide')
@st.cache_data(ttl=float(timedelta(minutes=5).total_seconds()))
def fetch_and_cache_data(url, params):
    # Fetch data from the API and cache it for 5 minute.

    return fetch_data(url, params)

def show_image_from_url(image_url):
    #Function to return HTML code for displaying an image from a URL
    return f'<img src="{image_url}" width="32" height="32" />'

def process_data(data):
    #Process the data and returns a formatted DataFrame.

    df = pd.DataFrame(data)

    latest_timestamp = max(df['last_updated'])
    latest_timestamp = datetime.strptime(latest_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y/%m/%d - %H:%M:%S UTC')

    selected_columns = [
        'image', 'market_cap_rank', 'symbol', 'name', 'current_price',
        'market_cap', 'total_volume', 'price_change_percentage_1h_in_currency',
        'price_change_percentage_24h_in_currency', 'price_change_percentage_7d_in_currency',
        'price_change_percentage_30d_in_currency', 'price_change_percentage_1y_in_currency',
        'sparkline_in_7d'
    ]
    column_names = ['Image', 'Rank', 'Symbol', 'Name', 'Current Price', 'Market Cap', '24h Volume', '1h %', '24h %', '7d %', '30d %', '1y %', 'Sparkline 7 Days']

    df = df[selected_columns]
    df.columns = column_names

    df['Image'] = df['Image'].apply(show_image_from_url)
    df['Current Price'] = df['Current Price'].apply(lambda x: '{:,.12f}'.format(x).rstrip('0').rstrip('.'))
    df['Market Cap'] = df['Market Cap'].apply(lambda x: '{:,.0f}'.format(x))
    df['24h Volume'] = df['24h Volume'].apply(lambda x: '{:,.0f}'.format(x))
    df['Symbol'] = df['Symbol'].str.upper()
    
    percentage_columns = ['1h %', '24h %', '7d %', '30d %', '1y %']
    df[percentage_columns] = df[percentage_columns].applymap(lambda x: '{:,.2f}'.format(x))

    df['Sparkline 7 Days'] = df.apply(lambda row: f'<img src="data:image/png;base64,{plot_sparkline(row["Sparkline 7 Days"]["price"], row["7d %"])}" width="100%" height="auto" />', axis=1)

    # Apply conditional formatting to the percentage change columns
    for col in percentage_columns:
       df[col] = df[col].apply(lambda x: f'<span style="font-weight: bold; color: {"green" if float(x.replace(",", "")) > 0 else "red" if float(x.replace(",", "")) < 0 else "grey"}; padding: 2px;">{x}</span>')

    return df, latest_timestamp

data = fetch_and_cache_data(COINGECKO_API_URL, PARAMS)


if data:
    df, latest_timestamp = process_data(data)
    st_autorefresh(interval=60*1000*5, key="autorefresh")
    # Header
    header = f"""
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="flex-grow: 1;">
                <h1 style="margin: 0; white-space: nowrap;">Cryptocurrencies Live Prices</h1>
            </div>
            <div style="display: flex; align-items: center;">
                <span style="font-weight: bold; white-space: nowrap;">Last Update: {latest_timestamp}</span>
                <span style="font-weight: bold; margin-left: 16px; white-space: nowrap;">Powered by</span>
                <img src="{COINGECKO_LOGO_URL}" alt="CoinGecko Logo" style="height: 40px; margin-left: 8px;" />
            </div>
        </div>
        """

    st.markdown(header, unsafe_allow_html=True)

    # Add a search bar for filtering cryptocurrencies
    search_term = st.text_input("Search for a cryptocurrency (name or symbol):")
    # Filter the DataFrame based on the search term (case-insensitive)
    if search_term:
        df = df[df["Name"].str.contains(search_term, case=False) | df["Symbol"].str.contains(search_term, case=False)]

    #Table
    st.markdown("""
        <style>
            table {
                border-collapse: collapse;
                width: 100%; 
                font-size: 15px; 
                font-family: 'Roboto', sans-serif;  
            }
            th, td {
                border: 1px solid #555;
                padding: 0px 0px;
                text-align: left;
                color: #d5cbc6;
            }
            th {
                background-color: #2a3439;
            }
            tr:nth-child(even) {
                background-color: #28353b;
            }
            tr:nth-child(odd) {
                background-color: #2b3438;
            }
            tr:hover {
                background-color: #323232;
            }
            th:nth-child(4), th:nth-child(5),
            td:nth-child(4), td:nth-child(5) {
                font-weight: bold;
            }
            th:nth-child(6), th:nth-child(7),
            td:nth-child(6), td:nth-child(7) {
                font-style: italic;
                text-align: right;
            }
            th:nth-child(13), th:nth-child(13),
            td:nth-child(13), td:nth-child(13) {
                text-align: center;
            }
        </style>
        """, unsafe_allow_html=True)

    # Display table with images
    st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
else:
    st.error("No data available. Please try again later.")