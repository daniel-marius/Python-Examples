import datetime as dt

import matplotlib.pyplot as plt
import pandas_datareader as web

crypto = "BTC"
currency = "USD"

start = dt.datetime(2021, 2, 1)
end = dt.datetime.now()

data = web.DataReader(f"{crypto}-{currency}", "yahoo", start, end)
data2 = web.DataReader(f"ETH-{currency}", "yahoo", start, end)

plt.yscale("log")

plt.plot(data['Close'], label="BTC")
plt.plot(data2['Close'], label="ETH")
plt.legend(loc="upper left")
plt.show()

# plt.plot(data['Close'])
# plt.show()

# mpf.plot(data, type="candle", volume=True, style="yahoo")
