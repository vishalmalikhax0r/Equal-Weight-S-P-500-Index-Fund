# -*- coding: utf-8 -*-
"""Equal-Weight S&P 500 Index Fund.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Nc7cD5qqfj_cTOqA_Lz6slSlpLkjc-yR

## Equal-Weight S&P 500 Index Fund
"""

!pip install xlsxwriter

import numpy as np #The Numpy numerical computing library #it is faster than python because library is built of c or c++
import pandas as pd #The Pandas data science library
import requests #The requests library for HTTP requests in Python
import xlsxwriter #The XlsxWriter libarary for
import math #The Python math module

stocks = pd.read_csv('sp_500_stocks.csv')
stocks

IEX_CLOUD_API_TOKEN = 'sk_cf3780ff59204ed2aaeb77f8fcbd1866'

symbol = 'AAPL'
api_url = f'https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={IEX_CLOUD_API_TOKEN}'
response = requests.get(api_url)
data = response.json()
print(data)

print(data['latestPrice'])
print(data['marketCap'])

my_columns = ['Ticker', 'Stock Price', ' Market Capitalization', 'Number of Shares to Buy']
final_dataframe = pd.DataFrame(columns = my_columns)
final_dataframe

# Create a DataFrame from the data
new_data = pd.DataFrame([[symbol, data['latestPrice'], data['marketCap'], 'N/A']], columns=my_columns)

# Concatenate new_data with final_dataframe
final_dataframe = pd.concat([final_dataframe, new_data], ignore_index=True)
final_dataframe

# Function sourced from
# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
#     print(symbol_strings[i])

final_dataframe = pd.DataFrame(columns = my_columns)

for symbol_string in symbol_strings:
    batch_api_call_url = f'https://cloud.iexapis.com/stable/stock/market/batch/?types=quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()

    for symbol in symbol_string.split(','):
        # Check if the symbol exists in the data
        if symbol in data:
            # Check if quote information is available for the symbol
            if 'quote' in data[symbol]:
                latest_price = data[symbol]['quote']['latestPrice']
                market_cap = data[symbol]['quote']['marketCap']
                # Create a DataFrame with the data for the current symbol
                new_data = pd.DataFrame([[symbol, latest_price, market_cap, 'N/A']], columns=my_columns)
                # Concatenate new_data with final_dataframe
                final_dataframe = pd.concat([final_dataframe, new_data], ignore_index=True)
            else:
                print(f"No quote information found for symbol: {symbol}")
        else:
            print(f"Symbol '{symbol}' not found in data")

# Display the final DataFrame
final_dataframe

"""## Calculating the Number of Shares to Buy"""

portfolio_size = input("Enter the value of your portfolio:")

try:
    val = float(portfolio_size)
except ValueError:
    print("That's not a number! \n Try again:")
    portfolio_size = input("Enter the value of your portfolio:")

position_size = float(portfolio_size) / len(final_dataframe.index)
for i in range(0, len(final_dataframe['Ticker'])-1):
    final_dataframe.loc[i, 'Number Of Shares to Buy'] = math.floor(position_size / final_dataframe['Stock Price'][i])
final_dataframe

"""## Formatting Our Excel Output"""

writer = pd.ExcelWriter('recommended_trades.xlsx', engine='xlsxwriter')
final_dataframe.to_excel(writer, sheet_name='Recommended Trades', index = False)

background_color = '#0a0a23'
font_color = '#ffffff'

string_format = writer.book.add_format(
        {
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

dollar_format = writer.book.add_format(
        {
            'num_format':'$0.00',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

integer_format = writer.book.add_format(
        {
            'num_format':'0',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

# Access the workbook object from XlsxWriter
workbook  = writer.book
column_formats = {
                    'A': ['Ticker', string_format],
                    'B': ['Price', dollar_format],
                    'C': ['Market Capitalization', dollar_format],
                    'D': ['Number of Shares to Buy', integer_format]
                    }

for column in column_formats.keys():
    writer.sheets['Recommended Trades'].set_column(f'{column}:{column}', 20, column_formats[column][1])
    writer.sheets['Recommended Trades'].write(f'{column}1', column_formats[column][0], string_format)

print(writer.sheets['Recommended Trades'])

for column in column_formats.keys():
    print(f"Column: {column}, Header: {column_formats[column][0]}, Format: {column_formats[column][1]}")

# Close the workbook to save the file
workbook.close()

from google.colab import files

files.download('recommended_trades.xlsx')