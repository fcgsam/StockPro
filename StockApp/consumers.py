import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import yfinance as yf
from forex_python.converter import CurrencyCodes
import re
import urllib.parse

def sanitize_symbol(symbol):
    # Remove invalid characters
    return re.sub(r'[^a-zA-Z0-9_.-]', '', symbol)

class StockConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.symbol = self.scope['url_route']['kwargs']['symbol']
        self.room_group_name = f'stock_{self.symbol}'

        # Join group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send initial stock data
        await self.send_stock_data()

        # Periodically send updated data every 10 seconds (or as desired)
        self.update_task = asyncio.create_task(self.send_periodic_updates())

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        if hasattr(self, 'update_task'):
            self.update_task.cancel()

    async def send_stock_data(self):
        stock = yf.Ticker(self.symbol)
        stock_info = stock.info

        current_price = stock_info.get('currentPrice', 0)  # Default to 0 for calculations
        previous_close = stock_info.get('regularMarketPreviousClose', 0)
        currency_code = stock_info.get('currency', '')  # Get the currency code

        # Get currency symbol using CurrencyCodes
        currency_symbol = CurrencyCodes().get_symbol(currency_code) if currency_code else ''

        # Calculate value change and percentage change
        if previous_close != 0:
            value_change = current_price - previous_close
            percentage_change = (value_change / previous_close) * 100
        else:
            value_change = 0
            percentage_change = 0

        # Round values
        current_price = round(current_price, 2)
        value_change = round(value_change, 2)
        percentage_change = round(percentage_change, 2)
        print("percentage_change :",percentage_change)
        # Determine color
        color = 'green' if value_change >= 0 else 'red'
        live_data = stock.history(period='1d', interval='1m')  # Real-time with 1-minute intervals
        if not live_data.empty:
                dates = live_data.index.strftime('%Y-%m-%d %H:%M:%S').tolist()
                prices = live_data['Close'].tolist()
        # Send updated stock data to WebSocket
        await self.send(text_data=json.dumps({
            'symbol': self.symbol,
            'current_price': f"{currency_symbol}{current_price}",  # Include currency symbol
            'value_change': f"{currency_symbol}{value_change}",  # Include currency symbol
            'percentage_change': f"{percentage_change}%",  # Include percentage symbol
            'color': color,  # Add color info
            'realTime': True,
            'dates': dates,
            'prices': prices,
            'previousClose':previous_close
        }))
        
                
    async def send_periodic_updates(self):
        while True:
            await asyncio.sleep(10)  # Adjust the interval as needed
            await self.send_stock_data()
  

nifty_indices = {
    "Nifty 50": "^NSEI",
    "Nifty Bank": "^NSEBANK",
    "Nifty IT": "^CNXIT",
    "Nifty FMCG": "^CNXFMCG",
    "Nifty Auto": "^CNXAUTO",
    "Nifty Realty": "^CNXREALTY",
    "Nifty Metal": "^CNXMETAL",
    "Nifty Media": "^CNXMEDIA",
    "Nifty Energy": "^CNXENERGY",
    "Nifty Infrastructure": "^CNXINFRA",
    "BSE Sensex": "^BSESN",
}


def check_market_status(exchange):
    exchange_code = exchange_map.get(exchange)
    if not exchange_code:
        return f"Exchange {exchange} is not supported."
    
    # Try to get the market calendar for the exchange
    try:
        market_calendar = mcal.get_calendar(exchange_code)
    except Exception as e:
        return f"Error retrieving calendar for {exchange}: {e}"

    # Get today's date and a date range
    today = dt.date.today()
    today_datetime = dt.datetime.combine(today, dt.datetime.min.time())
    tomorrow_datetime = today_datetime + dt.timedelta(days=1)

    # Fetch market schedule between today and tomorrow
    schedule = market_calendar.schedule(start_date=today_datetime, end_date=tomorrow_datetime)
    
    if schedule.empty:
        return False
    
    # Get the market open and close times for today
    market_open = schedule.iloc[0]['market_open']
    market_close = schedule.iloc[0]['market_close']
    
    # Get the current time in the appropriate timezone
    now = dt.datetime.now(market_calendar.tz)

    # Check if the current time is within market hours
    if market_open <= now <= market_close:
        return True
    else:
        return False

exchange_map = {
    'NSE': 'XNSE',
    'NSI': 'XNSE',
    'BSE': 'XBOM',
    'BOM': 'XBOM',
    'NMS': 'NASDAQ',
    'NAS': 'NASDAQ',
    'NYQ': 'XNYS',
    'NYE': 'XNYS',
    'TSE': 'XTSE',
    'TSX': 'XTSE',
    'LSE': 'XLON',
    'LON': 'XLON',
    'AMS': 'XAMS',
    'BRU': 'XBRU',
    'PAR': 'XPAR',
    'MIL': 'XMIL',
    'JPX': 'XJPX',
    'TYO': 'XTKS',
    'HKG': 'XHKG',
    'SHA': 'XSHG',
    'SHE': 'XSHE',
    'KRX': 'XKRX',
    'ASX': 'XASX',
    'SGX': 'XSES',
    'TSE_JP': 'XTKS',
    'OTC': 'OTCM',
    'XETR': 'XETR',
    'FRA': 'XFRA',
    'SWX': 'XSWX',
    'STO': 'XSTO',
    'HELS': 'XHEL',
    'ICE': 'XICE',
    'OSE': 'XOSL',
    'WSE': 'XWAR',
    'SAO': 'BVMF',
    'JSE': 'XJSE',
    'TADAWUL': 'XSAU',
    'TEL': 'XTAE',
    'MEX': 'XMEX',
    'VIE': 'XWBO',
    'NZX': 'XNZE',
    'IST': 'XIST',
    'KLS': 'XKLS',
    'BKK': 'XBKK',
    'BVMF': 'BVMF',
}

class IndexStockConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Retrieve and decode the index_name
        raw_index_name = self.scope['url_route']['kwargs']['indexName']
        self.index_name = urllib.parse.unquote(raw_index_name)  # Decode the URL-encoded value

        # Get symbol from the dictionary
        self.symbol = nifty_indices.get(self.index_name)
        if not self.symbol:
            # Close the connection if the symbol is not found
            await self.close()
            return

        cleaned_symbol = re.sub(r'[^a-zA-Z0-9_.-]', '_', self.symbol)  # Replace invalid characters with underscores
        self.room_group_name = f'stock_{cleaned_symbol}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        await self.send_stock_data(self.symbol)
        
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def send_stock_data(self):
        stock = yf.Ticker(self.symbol)
        stock_info = stock.info
        print(stock_info)
        current_price = stock_info.get('regularMarketPrice', 0)
        previous_close = stock_info.get('regularMarketPreviousClose', 0)
        currency_code = stock_info.get('currency', '')
        print("prices :",current_price,previous_close,currency_code)
        # Get currency symbol
        currency_symbol = CurrencyCodes().get_symbol(currency_code) if currency_code else ''

        if previous_close != 0:
            value_change = current_price - previous_close
            percentage_change = (value_change / previous_close) * 100
        else:
            value_change = 0
            percentage_change = 0

        current_price = round(current_price, 2)
        value_change = round(value_change, 2)
        percentage_change = round(percentage_change, 2)

        color = 'green' if value_change >= 0 else 'red'

        await self.send(text_data=json.dumps({
            'symbol': self.symbol,
            'current_price': f"{currency_symbol}{current_price}",
            'value_change': f"{currency_symbol}{value_change}",
            'percentage_change': f"{percentage_change}%",
            'color': color,
        }))

    async def send_periodic_updates(self):
        while True:
            await asyncio.sleep(10)  # Adjust the interval as needed
            await self.send_stock_data()

import pandas_market_calendars as mcal
import datetime as dt
exchange_map = {
    'NSE': 'XNSE',
    'NSI': 'XNSE',
    'BSE': 'XBOM',
    'BOM': 'XBOM',
    'NMS': 'NASDAQ',
    'NAS': 'NASDAQ',
    'NYQ': 'XNYS',
    'NYE': 'XNYS',
    'TSE': 'XTSE',
    'TSX': 'XTSE',
    'LSE': 'XLON',
    'LON': 'XLON',
    'AMS': 'XAMS',
    'BRU': 'XBRU',
    'PAR': 'XPAR',
    'MIL': 'XMIL',
    'JPX': 'XJPX',
    'TYO': 'XTKS',
    'HKG': 'XHKG',
    'SHA': 'XSHG',
    'SHE': 'XSHE',
    'KRX': 'XKRX',
    'ASX': 'XASX',
    'SGX': 'XSES',
    'TSE_JP': 'XTKS',
    'OTC': 'OTCM',
    'XETR': 'XETR',
    'FRA': 'XFRA',
    'SWX': 'XSWX',
    'STO': 'XSTO',
    'HELS': 'XHEL',
    'ICE': 'XICE',
    'OSE': 'XOSL',
    'WSE': 'XWAR',
    'SAO': 'BVMF',
    'JSE': 'XJSE',
    'TADAWUL': 'XSAU',
    'TEL': 'XTAE',
    'MEX': 'XMEX',
    'VIE': 'XWBO',
    'NZX': 'XNZE',
    'IST': 'XIST',
    'KLS': 'XKLS',
    'BKK': 'XBKK',
    'BVMF': 'BVMF',
}

def check_market_status(exchange):
    exchange_code = exchange_map.get(exchange)
    if not exchange_code:
        return f"Exchange {exchange} is not supported."
    
    # Try to get the market calendar for the exchange
    try:
        market_calendar = mcal.get_calendar(exchange_code)
    except Exception as e:
        return f"Error retrieving calendar for {exchange}: {e}"

    # Get today's date and a date range
    today = dt.date.today()
    today_datetime = dt.datetime.combine(today, dt.datetime.min.time())
    tomorrow_datetime = today_datetime + dt.timedelta(days=1)

    # Fetch market schedule between today and tomorrow
    schedule = market_calendar.schedule(start_date=today_datetime, end_date=tomorrow_datetime)
    
    if schedule.empty:
        return False
    
    # Get the market open and close times for today
    market_open = schedule.iloc[0]['market_open']
    market_close = schedule.iloc[0]['market_close']
    
    # Get the current time in the appropriate timezone
    now = dt.datetime.now(market_calendar.tz)

    # Check if the current time is within market hours
    if market_open <= now <= market_close:
        return True
    else:
        return False

def fetch_intraday_data(symbol):
    today = dt.datetime.now().date()
    ticker = yf.Ticker(symbol)

    # Fetch intraday data with 1-minute intervals
    intraday_data = ticker.history(period='1d', interval='1m')
    return intraday_data
class OneStockConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.symbol = self.scope['url_route']['kwargs']['symbol']
        self.room_group_name = f'stock_{self.symbol}'

        if not check_market_status(self.symbol):  # Check if the market is open
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Send initial stock data
        await self.send_initial_data()

        # Start periodic updates
        self.update_task = asyncio.create_task(self.send_periodic_updates())

    async def send_initial_data(self):
        intraday_data = fetch_intraday_data(self.symbol)
        if not intraday_data.empty:
            await self.send(text_data=json.dumps({
                'intraday_data': intraday_data['Close'].to_list(),
                'timestamps': intraday_data.index.strftime('%Y-%m-%d %H:%M').to_list(),
            }))

    async def send_stock_data(self):
        stock = yf.Ticker(self.symbol)
        intraday_data = stock.history(period='1d', interval='1m')
        current_price = intraday_data['Close'].iloc[-1] if not intraday_data.empty else 0

        await self.send(text_data=json.dumps({
            'current_price': current_price,
            'intraday_data': intraday_data['Close'].to_list(),
            'timestamps': intraday_data.index.strftime('%Y-%m-%d %H:%M').to_list(),
        }))

    async def send_periodic_updates(self):
        while True:
            await asyncio.sleep(10)  # Update every 10 seconds
            await self.send_stock_data()
