# Cryptocurrency Live Prices Streamlit App

This app displays live prices of cryptocurrencies using the CoinGecko API. It is a Streamlit project created by PyFiHub.

## Information

- Date: 2023-05-09
- Version: 1.0
- Author: PyFiHub

## Setup

The app uses the following libraries:

- `requests`
- `pandas`
- `streamlit`
- `datetime`
- `timedelta`
- `streamlit_autorefresh`
- `base64`
- `io`
- `matplotlib.pyplot`

## Usage

To run the app, execute the following command:
```python
streamlit run app.py
```


- The app will display a table of the top 100 cryptocurrencies by market capitalization, along with their current price, market cap, 24h volume, and percentage changes over the last hour, 24 hours, 7 days, 30 days, and 1 year.

- The app also features a search bar for filtering cryptocurrencies by name or symbol.

- The table includes sparklines of the 7-day price history for each cryptocurrency, with the line color indicating whether the 7-day percentage change is positive (green), negative (red), or neutral (gray).

- The app automatically refreshes every 5 minutes to display the latest data from the CoinGecko API.
