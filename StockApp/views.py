import pandas as pd
import pandas_market_calendars as mcal
import datetime as dt
import requests
from django.shortcuts import render
import yfinance as yf
import math  # Import the math module

# List of Nifty indices with their symbols
nifty_indices = {
    "Nifty 50": "^NSEI",
    "Nifty Bank": "^NSEBANK",
    "Nifty IT": "^CNXIT",
    # "Nifty Financial Services": "^CNXFIN",
    "Nifty FMCG": "^CNXFMCG",
    # "Nifty Pharma": "^CNXPHARMA",
    "Nifty Auto": "^CNXAUTO",
    "Nifty Realty": "^CNXREALTY",
    "Nifty Metal": "^CNXMETAL",
    "Nifty Media": "^CNXMEDIA",
    "Nifty Energy": "^CNXENERGY",
    # "Nifty Commodities": "^CNXCOMMOD",
    "Nifty Infrastructure": "^CNXINFRA",
    # "Nifty Consumption": "^CNXCONS",
    "BSE Sensex": "^BSESN",
    # "BSE Smallcap": "^BSESMCAP",
    # "BSE Midcap": "^BSEMDCP",

    # International Indices
    # "Dow Jones Industrial Average": "^DJI",
    # "S&P 500": "^GSPC",
    # "NASDAQ Composite": "^IXIC",
    # "FTSE 100": "^FTSE",
    # "DAX (Germany)": "^GDAXI",
    # "CAC 40 (France)": "^FCHI",
    # "Nikkei 225 (Japan)": "^N225",
    # "Hang Seng (Hong Kong)": "^HSI",
    # "Shanghai Composite": "000001.SS",
    # "KOSPI (South Korea)": "^KS11",
    # "S&P/TSX Composite (Canada)": "^GSPTSE",
    # "ASX 200 (Australia)": "^AXJO",
    # # "MSCI World": "^MSCIW",
    # "Euro Stoxx 50": "^STOXX50E",
    # # "S&P BSE Healthcare": "^BSEHC",
    # "Russell 2000": "^RUT",
    # "Bovespa (Brazil)": "^BVSP"
}

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

market_hours = {
        "NYSE": {
            "country": "United States",
            "hours": {
                "open": "09:30:00",
                "close": "16:00:00",
                "pre_market": "04:00:00 - 09:30:00",
                "after_hours": "16:00:00 - 20:00:00"
            }
        },
        "NASDAQ": {
            "country": "United States",
            "hours": {
                "open": "09:30:00",
                "close": "16:00:00",
                "pre_market": "04:00:00 - 09:30:00",
                "after_hours": "16:00:00 - 20:00:00"
            }
        },
        "LSE": {
            "country": "United Kingdom",
            "hours": {
                "open": "08:00:00",
                "close": "16:30:00"
            }
        },
        "TSE": {
            "country": "Japan",
            "hours": {
                "open": "09:00:00",
                "close": "15:00:00",
                "lunch_break": "11:30:00 - 12:30:00"
            }
        },
        "BSI": {
            "country": "India",
            "hours": {
                "open": "09:15:00",
                "close": "15:30:00",
                "pre_open": "09:00:00 - 09:15:00"
            }
        },
        "NSI": {
            "country": "India",
            "hours": {
                "open": "09:15:00",
                "close": "15:30:00",
                "pre_open": "09:00:00 - 09:15:00"
            }
        },
        "SSE": {
            "country": "China",
            "hours": {
                "open": "09:30:00",
                "close": "15:00:00",
                "lunch_break": "11:30:00 - 13:00:00"
            }
        },
        "EURONEXT": {
            "countries": ["France", "Netherlands", "Belgium"],
            "hours": {
                "open": "09:00:00",
                "close": "17:30:00"
            }
        },
        "ASX": {
            "country": "Australia",
            "hours": {
                "open": "10:00:00",
                "close": "16:00:00"
            }
        }
}

def generate_time_list(open_time, close_time, interval_minutes=5, breaks=None):
    start_time = datetime.strptime(open_time, "%H:%M:%S")
    end_time = datetime.strptime(close_time, "%H:%M:%S")
    
    # Print debug information
    print("Start time:", start_time, "End time:", end_time)

    
    # Generate the time list with the specified interval
    time_list = []
    current_time = start_time

    while current_time <= end_time:
        time_list.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=1)    # Use the interval_minutes parameter
        
    
    # Handle breaks if provided
    if breaks:
        for break_time in breaks:
            break_start = datetime.strptime(break_time[0], "%H:%M:%S")
            break_end = datetime.strptime(break_time[1], "%H:%M:%S")
            time_list = [t for t in time_list if not (break_start.strftime("%H:%M") <= t <= break_end.strftime("%H:%M"))]

    return time_list

# Example usage

# Function to check if the market is open
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

import yfinance as yf
from datetime import datetime, timedelta


def fetch_index_data_yahoo(symbol):
    try:
        ticker = yf.Ticker(symbol)
        index_info = ticker.info
        
        current_price = index_info.get('regularMarketPrice')  # Get the current market price
        previous_close = index_info.get('regularMarketPreviousClose')  # Get the previous day's closing price

        # Handle market open vs. closed
        if current_price is None:
            # Market is closed
            history = ticker.history(period='5d')
            if history.empty or len(history) < 2:
                print(f"Not enough historical data for {symbol}.")
                return {
                    "current_price": 'N/A',
                    "previous_close": 'N/A',
                    "percentage_change": 'N/A',
                    "value_change": 'N/A',
                    "symbol": symbol,
                    "color_status": 'N/A',
                    
                }

            last_dates = history.index[-2:].date
            last_closes = history['Close'].iloc[-2:].values
            last_trading_dates = [date for date in last_dates]
            last_closing_prices = [float(round(price, 2)) for price in last_closes]

            # Ensure we have at least two closing prices
            if len(last_closing_prices) < 2:
                print(f"Insufficient closing prices for {symbol}.")
                return {
                    "current_price": 'N/A',
                    "previous_close": 'N/A',
                    "percentage_change": 'N/A',
                    "value_change": 'N/A',
                    "symbol": symbol,
                    "color_status": 'N/A',
                    
                }
            
            historical_data = last_closing_prices[0]  # Fetch last day's closing price
           

            # If previous_close is None, fallback to historical data
            if previous_close is None:
                previous_close = historical_data
            
            value_change = last_closing_prices[1] - historical_data  # Example value; adjust as needed
            color_status = "green" if value_change >= 0 else "red"
            percentage_change = round((value_change / last_closing_prices[0]) * 100, 2) if last_closing_prices[0] else 0
            
            current_price = previous_close  # Use previous close as current price since market is closed
            
            return {
                "current_price": last_closing_prices[1],
                "previous_close": last_closing_prices[0],
                "percentage_change": percentage_change,
                "value_change": value_change,
                "symbol": symbol,
                "color_status": color_status,
                
            }
        else:
            # Market is open
            if current_price is None or previous_close is None:
                print(f"Warning: Current price or previous close is None for {symbol}")
                return {
                    "current_price": 'N/A',
                    "previous_close": 'N/A',
                    "percentage_change": 'N/A',
                    "value_change": 'N/A',
                    "symbol": symbol,
                    "color_status": 'N/A',
                    
                }
                
            value_change = current_price - previous_close
            color_status = "green" if value_change >= 0 else "red"
            percentage_change = round((value_change / previous_close) * 100, 2)

            return {
                "current_price": round(current_price, 2),
                "previous_close": round(previous_close, 2),
                "percentage_change": percentage_change,
                "value_change": value_change,
                "symbol": symbol,
                "color_status": color_status,
                
            }

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return {
            "current_price": 'N/A',
            "previous_close": 'N/A',
            "percentage_change": 'N/A',
            "value_change": 'N/A',
            "symbol": symbol,
            "color_status": 'N/A',
            
        }

# Example usage for the StockListPage function
def StockListPage(request):
    index_data = {name: fetch_index_data_yahoo(symbol) for name, symbol in nifty_indices.items()}
    return render(request, 'index.html', {'index_data': index_data})


import requests
import csv
from django.core.cache import cache
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
import json
from django.core.cache import cache
from forex_python.converter import CurrencyCodes
from django.http import Http404
API_KEY = 'cs1su59r01qsperufrggcs1su59r01qsperufrh0'  # Replace with your Finnhub API key
BASE_URL = 'https://finnhub.io/api/v1'

def fetch_stock_symbols():
    url = f"{BASE_URL}/stock/symbol?exchange=US&token={API_KEY}"  # Adjust exchange for Indian stocks
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses

        symbols = response.json()
        indian_symbols = []
        other_symbols = []
        
        for symbol in symbols:
            currency = symbol.get('currency', '').upper()
            description = symbol.get('description', '').lower()

            # Check for Indian stock market codes or keywords
            if currency == "INR":
                print("currency",currency)
                indian_symbols.append(symbol)
            else:
                other_symbols.append(symbol)

        # Prioritize Indian stocks first, followed by others
        prioritized_symbols = indian_symbols + other_symbols
        return prioritized_symbols

    except requests.exceptions.RequestException as e:
        print(f"Error fetching stock symbols: {e}")
        return []

def fetch_stock_prices(symbol):
    try:
        stock = yf.Ticker(symbol)
        stock_info = stock.info  # Get stock info
        
        if stock_info:  # Check if stock info is available
            current_price = round(stock_info.get('currentPrice', 0), 2)
            company_name = stock_info.get('longName', 'N/A')  # Get company name
            previous_close = round(stock_info.get('previousClose', 0), 2)
            currency_codes = CurrencyCodes()
            currency_code = stock_info.get('currency')
            currency_symbol = currency_codes.get_symbol(currency_code)
            print(currency_code,currency_symbol,company_name)
            if current_price and previous_close:
                price_change = round(current_price - previous_close, 2)
                percentage_change = round((price_change / previous_close) * 100, 2) if previous_close else 0
            else:
                price_change = None
                percentage_change = None
        else:
            current_price = None
            company_name = None
            price_change = None
            percentage_change = None
        
        return {
            'symbol': symbol,
            'company_name': company_name,
            'current_price': current_price,
            'price_change': price_change,
            'percentage_change': percentage_change,
            'currency_symbol':currency_symbol
        }
    except Exception as e:
        return {
            'symbol': symbol,
            'company_name': 'Error',
            'current_price': None,
            'price_change': None,
            'percentage_change': None,
            'currency_symbol':None
        }


def all_stocks(request):
    symbols = fetch_stock_symbols()
    stock_info = []
    valid_symbols = []
    all_symbols = json.dumps(symbols)
    if symbols:
        for i in symbols[:20]:  # Limiting to 10 symbols for performance (adjust as needed)
            
              # Filter out symbols with suffixes
            try:
                common_symbols = i['symbol'].split('.')[0]
            except:
                common_symbols = i['symbol']
          
            try:
                    stock_data = yf.Ticker(common_symbols)
                    # Attempt to fetch data for the symbol
                    if stock_data.info:  # If stock_data.info is not empty
                        valid_symbols.append(i['symbol'])
                    else:
                        print(f"No data found for symbol: {i['symbol']}")

            except Exception as e:
                    # Handle the case where the symbol does not exist or other errors
                    print(f"Error fetching data for symbol {i['symbol']}: {e}")




    for i in valid_symbols:
            stock_info.append(fetch_stock_prices(i))

      # Convert symbols list to JSON for the frontend

    return render(request, 'allStock.html', {'stock_details': stock_info, 'all_symbols': mark_safe(all_symbols)})

def load_more_stocks(request):
    if request.method == "POST":
        symbols = request.POST.getlist('symbols[]')
        
        stock_info = [fetch_stock_prices(symbol) for symbol in symbols]
        # html = render_to_string('partials/stock_list.html', {'stock_details': stock_info})
        # return JsonResponse({'html': html})
        return JsonResponse({'stock_details': stock_info})



def stock_detail(request, symbol):
    # Check if the data is already cached
    print("index :0 ",nifty_indices.get("symbol"))
    if nifty_indices.get(symbol):
        symbol = nifty_indices.get(symbol)
    
    cached_data = cache.get(symbol)
    market_open = ""
    if cached_data:
        return render(request, 'stockPage.html', cached_data)

    try:
        # Get stock information using yfinance
        stock = yf.Ticker(symbol)
        stock_info = stock.info
   
        history_c = stock.history(period='1d', interval='1m')

        # Format dates and extract closing prices
        dates = history_c.index.strftime('%Y-%m-%d').tolist()  # Format dates
        prices = history_c['Close'].tolist()  # Closing prices
        historical_data = stock.history(period='5d', interval='1d')
        if len(historical_data) >= 2:
            previous_day_close = historical_data['Close'].iloc[-2]  # Get close from 1 day ago
            print("Previous Day's Close:", previous_day_close)
        else:
            previous_day_close = None
            print("Not enough data to get previous day's close.")
        # Get the last 7 days of data
        if len(prices) > 0:
            last_day_prices = prices  # Last day prices
            last_day_dates = dates[-len(last_day_prices):]  # Corresponding dates
        else:
            last_day_prices, last_day_dates = [], []

        # Get the previous close price (last price before the last week's data)
        previous_week_close = prices[-8] if len(prices) > 7 else None  # This is the close before the last week

        
        # Ensure stock_info exists and is not None
        if not stock_info:
            raise ValueError(f"Stock info for symbol '{symbol}' is empty or not available")

        # Extract relevant data
      
        current_price = stock_info.get('currentPrice', None)
        previous_close = stock_info.get('regularMarketPreviousClose', None)
        currency_symbol = stock_info.get('currencySymbol', 'N/A')
        exchange = stock_info.get('exchange', 'Unknown')
        
        print("exchange :", exchange,previous_close)
        
        # Check if market is open
        if not check_market_status(exchange):
            # Market is closed
            print("market is close")
            market_open = "Close"
            history = stock.history(period='5d')
            prices_1m = stock.history(period='1d',interval='1m')['Close'].tolist()
            data_label = stock.history(period='5d', interval='1d')
            
            if len(data_label) >= 2:
                
                previous_close = data_label['Close'].iloc[-2]
                print("Previous Day's Close:", previous_close)
            else:
                print("Not enough data to calculate previous close.")
            if history.empty or len(history) < 2:
                print(f"Not enough historical data for {symbol}.")
                return render(request, 'stockPage.html', {'error': 'Not enough data available.'})

            last_closes = history['Close'].iloc[-2:].values
            last_closing_prices = [float(round(price, 2)) for price in last_closes]

            # Ensure we have at least two closing prices
            if len(last_closing_prices) < 2:
                print(f"Insufficient closing prices for {symbol}.")
                return render(request, 'stockPage.html', {'error': 'Insufficient closing prices.'})

            # Set previous close if it's None
            if previous_close is None:
                previous_close = last_closing_prices[0]

            # Use previous close as current price since market is closed
            current_price = last_closing_prices[1] if last_closing_prices else None

            # Calculate value change and percentage change
            if previous_close is not None:
                value_change = current_price - previous_close
                color_status = "green" if value_change >= 0 else "red"
                percentage_change = (value_change / previous_close * 100) if previous_close else 0
            else:
                value_change = percentage_change = None
       
        else:
            # print("Market is open", market_status)
            # print(stock_info)  
            # Attempt to fetch prices
            current_price = stock_info.get('currentPrice') or stock_info.get('regularMarketPrice')
            previous_close = stock_info.get('regularMarketPreviousClose')

            if current_price is None or previous_close is None:
                print(f"Warning: Current price or previous close is None for {symbol}")
                return render(request, 'stockPage.html', {'error': 'Unable to fetch current price.'})
            
            market_open = "Open"
            value_change = current_price - previous_close
            color_status = "green" if value_change >= 0 else "red"
            percentage_change = round((value_change / previous_close) * 100, 2) if previous_close else None

        # Fetch news articles
        news = stock.news  # Get news related to the stock
        events = stock.calendar  # Get upcoming events for the stock
        currency_codes = CurrencyCodes()
        currency_code = stock_info.get('currency', stock_info.get('currency'))
        currency_symbol = currency_codes.get_symbol(currency_code)
        if exchange in market_hours:
            open_time = market_hours[stock_info.get('exchange')]['hours']['open']
            closing_time = market_hours[stock_info.get('exchange')]['hours']['close']
            market_time = generate_time_list(open_time, closing_time, interval_minutes=1)
        else:
            print("line else")
            marketH = exchange_map[stock_info.get('exchange')]
            open_time = market_hours[marketH]['hours']['open']
            closing_time = market_hours[marketH]['hours']['close']
            market_time = generate_time_list(open_time, closing_time, interval_minutes=1)
        print(exchange," : eschange ")
        context = {
            'stock': {
                'name': stock_info.get('longName', stock_info.get('symbol', 'N/A')),
                'symbol': stock_info.get('symbol', 'N/A'),
                'current_price': round(current_price, 2) if current_price is not None else 'N/A',
                'value_change': round(value_change, 2) if value_change is not None else 'N/A',
                'percentage_change': round(percentage_change, 2) if percentage_change is not None else 'N/A',
                'market_cap': stock_info.get('marketCap', 'N/A'),
                'pe_ratio': stock_info.get('forwardPE', 'N/A'),
                'dividend_yield': stock_info.get('dividendYield', 'N/A'),
                'sector': stock_info.get('sector', 'N/A'),
                'industry': stock_info.get('industry', 'N/A'),
                'website': stock_info.get('website', 'N/A'),
                'company_summary': stock_info.get('longBusinessSummary', 'No summary available.'),
                'shareholder_details': {
                    'held_percent_insiders': stock_info.get('heldPercentInsiders', 'N/A'),
                    'held_percent_institutions': stock_info.get('heldPercentInstitutions', 'N/A'),
                    'total_shares_outstanding': stock_info.get('sharesOutstanding', 'N/A'),
                },
                'company_officers': [
                    {
                        'name': officer.get('name', 'N/A'),
                        'title': officer.get('title', 'N/A'),
                        'age': officer.get('age', 'N/A'),
                        'total_pay': officer.get('totalPay', 'N/A'),
                    }
                    for officer in stock_info.get('companyOfficers', [])
                ],
                'color_status': color_status,
                'news': news,  # Add news data to context
                'events': events,  # Add events data to context
                'currency_symbol': currency_symbol,
                "market_open": market_open,
                'historical_data': {
                    'dates': last_day_dates,
                    'prices': last_day_prices,
                },
                'previous_close_price': previous_week_close,
                'fiftyTwoWeekLow':stock_info.get('fiftyTwoWeekLow',None),
                'fiftyTwoWeekHigh':stock_info.get('fiftyTwoWeekHigh',None),
                'total_cash': stock_info.get('totalCash', 'N/A'),
                'total_cash_per_share': stock_info.get('totalCashPerShare', 'N/A'),
                'ebitda': stock_info.get('ebitda', 'N/A'),
                'total_debt': stock_info.get('totalDebt', 'N/A'),
                'total_revenue': stock_info.get('totalRevenue', 'N/A'),
                'debt_to_equity': stock_info.get('debtToEquity', 'N/A'),
                'revenue_per_share': stock_info.get('revenuePerShare', 'N/A'),
                'earnings_growth': stock_info.get('earningsGrowth', 'N/A'),
                'revenue_growth': stock_info.get('revenueGrowth', 'N/A'),
                'gross_margins': stock_info.get('grossMargins', 'N/A'),
                'ebitda_margins': stock_info.get('ebitdaMargins', 'N/A'),
                'operating_margins': stock_info.get('operatingMargins', 'N/A'),
                'financial_currency': stock_info.get('financialCurrency', 'N/A'),
                'trailing_peg_ratio': stock_info.get('trailingPegRatio', 'N/A'),
                'previous_day_close':previous_day_close,
                'market_time':market_time
            }   
        }

        # Cache the data for 5 minutes
        cache.set(symbol, context, timeout=300)

        return render(request, 'stockPage.html', context)

    except (KeyError, IndexError, ValueError) as e:
        # Handle specific cases where stock data is invalid or missing
        print(f"Error fetching stock data for {symbol}: {e}")
        raise Http404(f"Stock data for '{symbol}' not found")

    except Exception as e:
        # Log any unexpected exceptions for debugging
        print(f"An error occurred while fetching stock data: {e}")
        return render(request, 'stockPage.html', {'error': 'Unable to fetch stock data. Please try again later.'})

from django.http import JsonResponse, Http404


from datetime import datetime, timedelta
import pytz  # Ensure you have pytz installed


# Period mapping
period_mapping = {
    '1d': '1d',
    '1w': '5d',
    '1mo': '1mo',
    '3mo': '3mo',
    '1yr': '1y',
    '5yr': '5y',
    'max': 'max'  # Use None to fetch all available data
}


def get_previous_close(symbol, start_date):
    """Fetches the previous close price for the last available trading day before the start_date."""
    utc_tz = pytz.UTC
    start_date_obj = utc_tz.localize(datetime.strptime(start_date, '%Y-%m-%d'))
    max_attempts = 10  # Limit the number of attempts to find a previous trading day
    attempts = 0

    while attempts < max_attempts:
        previous_day = start_date_obj - timedelta(days=1)
        historical_data = yf.Ticker(symbol).history(
            start=previous_day.strftime('%Y-%m-%d'),
            end=(previous_day + timedelta(days=1)).strftime('%Y-%m-%d')
        )

        # Check if the historical data is empty
        print(historical_data)
        if not historical_data.empty:
            return historical_data['Close'].iloc[0]

        start_date_obj = previous_day
        attempts += 1

    return None

from datetime import datetime, timedelta


def stock_history_dynamic(request, symbol, period):
    # Normalize the period using the mapping
    period_key = period_mapping.get(period)
    stock = yf.Ticker(symbol) 
    info = stock.info

    exchange = info.get('exchange')
    market_time= None
    if period_key == '1d':
        if exchange in market_hours:
            open_time = market_hours[info.get('exchange')]['hours']['open']
            closing_time = market_hours[info.get('exchange')]['hours']['close']
            market_time = generate_time_list(open_time, closing_time, interval_minutes=1)
        else:
            marketH = exchange_map[info.get('exchange')]
            open_time = market_hours[marketH]['hours']['open']
            closing_time = market_hours[marketH]['hours']['close']
            market_time = generate_time_list(open_time, closing_time, interval_minutes=1)
    print(f"Exchange: {info.get('exchange')}")

    if period_key == '1d' and check_market_status(info.get('exchange')):
        # If market is open, fetch real-time data
        live_data = stock.history(period='1d', interval='1m')  # Real-time with 1-minute intervals
        data = stock.history(period='5d', interval='1d')
  
        if len(data) >= 2:
                
                previous_close = data['Close'].iloc[-2]
                print("Previous Day's Close:", previous_close)
        else:
                print("Not enough data to calculate previous close.")
        if live_data.empty:
            return JsonResponse({'error': 'No real-time data found'}, status=404)
        
        # Extract real-time dates and prices
        dates = live_data.index.strftime('%Y-%m-%d %H:%M:%S').tolist()
        prices = live_data['Close'].tolist()
        
        response_data = {
            'dates': dates,
            'prices': prices,
            'realTime': True,
            'market_time':market_time,
            'previousClose':previous_close
            
        }
        return JsonResponse(response_data)
    else:
        # If market is closed or period is not '1d', return historical data
        if period_key is None:
            return JsonResponse({'error': 'Invalid period'}, status=400)

        # Fetch historical data using yfinance
        if period_key:
            historical_data = stock.history(period=period_key)
        else:
            historical_data = stock.history()

        # Check if historical data is empty
        if historical_data.empty:
            return JsonResponse({'error': 'No data found'}, status=404)

        # Extract dates and prices
        if period_key == '1d':
            dates = None
            prices = stock.history(period='1d',interval='1m')['Close'].tolist()
            data = stock.history(period='5d', interval='1d')

            if len(data) >= 2:
                
                previous_close = data['Close'].iloc[-2]
                print("Previous Day's Close:", previous_close)
            else:
                print("Not enough data to calculate previous close.")
        else:
            dates = historical_data.index.strftime('%Y-%m-%d').tolist()
            prices = historical_data['Close'].tolist()
            previous_close = get_previous_close(symbol, dates[0])
        
        response_data = {
            'dates': dates,
            'prices': prices,
            'previousClose': previous_close,
            'realTime': False,
            'market_time':market_time,
        }

        return JsonResponse(response_data)