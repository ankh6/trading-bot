from orders.Order import Side
import csv

def _create_trading_report(date, symbol: str, short_ema: int, long_ema: int, rsi: int, side: Side):
    fieldnames = ["Date", "trading pair", "Short EMA", "Long EMA", "RSI", "Side"]
    with open("trading-report.csv", mode='a', newline='\n') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'Date': date, "trading pair": symbol, "Short EMA": short_ema, "Long EMA": long_ema,"RSI": rsi, "Side": side})
