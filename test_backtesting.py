from backtesting import Backtest, Strategy
import talib
import pandas as pd

#Descargamos los datos

data = pd.read_csv("BTC-2022-2M.csv")
data["Date"] = pd.DatetimeIndex(data["Date"])
data = data.set_index("Date")

close = data.Close.values

data

class EMAcross(Strategy):
    def init(self):
        self.ema30 = self.I(talib.EMA,self.data.Close,50)
        self.ema75 = self.I(talib.EMA,self.data.Close,608)
        self.ema100 = self.I(talib.EMA,self.data.Close,1008)
        self.ema200 = self.I(talib.EMA,self.data.Close,2008)
        self.pasoUno = 0
        self.pasoDos = 0
        self.pasoTres = 0

    def should_skip_day(self):
        # Obtén el día de la semana (0 = lunes, 6 = domingo)
        weekday = self.data.index[-1].weekday()
        current_hour = self.data.index[-1].hour
        current_month = self.data.index[-1].month
        # Devuelve True si es sábado (5) o domingo (6), de lo contrario, False
        return (weekday in [5, 6] or current_hour >= 21 or current_hour <= 13)

    def next(self):
        price = self.data.Close[-1]

        if self.should_skip_day():
            return

        if self.ema30[-1] < self.ema75[-1] and self.ema30[-1] > self.ema100[-1] and not self.position.is_short:
            self.pasoUno = 1

        if self.pasoUno > 0 and self.ema30[-1] < self.ema100[-1] and self.ema75[-1] < self.ema100[-1]:
            if self.ema30[-1] < self.ema75[-1]:
                self.pasoDos = 1
            else:
                self.pasoUno = 0
                self.pasoDos = 0

        if self.pasoUno > 0 and self.pasoDos > 0 and price > self.ema100[-1] and self.ema100[-1] < self.ema200[-1]:
            self.pasoTres = 1

        if self.pasoTres > 0 and price > self.ema200[-1]:
            self.pasoUno = 0
            self.pasoDos = 0
            self.pasoTres = 0

        if self.pasoTres > 0 and price < self.ema75[-1]:
            self.buy(limit = None, sl = price*0.992, tp = price*1.24)
            self.pasoUno = 0
            self.pasoDos = 0
            self.pasoTres = 0


bt = Backtest(data,EMAcross,cash = 100000, exclusive_orders=True)

#Ejecutamos el backtest
stats = bt.run()

print(stats)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

print(stats._trades)
