from backtesting import Backtest, Strategy
import talib
import pandas as pd
import matplotlib.pyplot as plt

#Descargamos los datos

data = pd.read_csv("BTC-2017-2M.csv")
data["Date"] = pd.DatetimeIndex(data["Date"])
data = data.set_index("Date")

close = data.Close.values

data

class EMAcross(Strategy):
    def init(self):
        self.ema30 = self.I(talib.EMA,self.data.Close,30)
        self.ema75 = self.I(talib.EMA,self.data.Close,75)
        self.ema100 = self.I(talib.EMA,self.data.Close,100)
        self.ema200 = self.I(talib.EMA,self.data.Close,200)
        self.pasoUno = 0
        self.pasoDos = 0
        self.pasoTres = 0

    def should_skip_day(self):
        # Obtén el día de la semana (0 = lunes, 6 = domingo)
        weekday = self.data.index[-1].weekday()
        # Devuelve True si es sábado (5) o domingo (6), de lo contrario, False
        return weekday in [5, 6]

    def next(self):
        price = self.data.Close[-1]

        if self.should_skip_day():
            return

        if self.ema30[-1] > self.ema75[-1] and self.ema30[-1] < self.ema100[-1] and not self.position.is_long:
            self.pasoUno = 1

        if self.pasoUno > 0 and self.ema30[-1] > self.ema100[-1] and self.ema75[-1] > self.ema100[-1]:
            if self.ema30[-1] > self.ema75[-1]:
                self.pasoDos = 1
            else:
                self.pasoUno = 0
                self.pasoDos = 0

        if self.pasoUno > 0 and self.pasoDos > 0 and price < self.ema100[-1] and self.ema100[-1] > self.ema200[-1]:
            self.pasoTres = 1

        if self.pasoTres > 0 and price < self.ema200[-1]:
            self.pasoUno = 0
            self.pasoDos = 0
            self.pasoTres = 0

        if self.pasoTres > 0 and price > self.ema75[-1]:
            self.buy(limit = None, sl = price*0.992, tp = price*1.04)
            self.pasoUno = 0
            self.pasoDos = 0
            self.pasoTres = 0

bt = Backtest(data,EMAcross,cash = 100000, exclusive_orders=True)

#Ejecutamos el backtest
stats = bt.run()

#Vamos los resultados del backtest
print(stats)

#bt.plot()
