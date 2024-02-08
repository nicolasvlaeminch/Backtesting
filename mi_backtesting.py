from backtesting import Backtest, Strategy
import talib
import pandas as pd

#Descargamos los datos

data = pd.read_csv("BTC-2017-2M.csv")
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
        self.pasoUnoCompra = 0
        self.pasoDosCompra = 0
        self.pasoTresCompra = 0
        self.pasoUnoVenta = 0
        self.pasoDosVenta = 0
        self.pasoTresVenta = 0

    def should_skip_day(self):
        # Obtén el día de la semana (0 = lunes, 6 = domingo)
        weekday = self.data.index[-1].weekday()
        current_hour = self.data.index[-1].hour
        current_month = self.data.index[-1].month
        # Devuelve True si es sábado (5) o domingo (6), de lo contrario, False
        return (weekday in [5, 6] or current_hour <= 13 or current_hour >= 21)

    def next(self):
        price = self.data.Close[-1]

        if self.should_skip_day():
            return

        if self.ema30[-1] > self.ema75[-1] and self.ema30[-1] < self.ema100[-1] and not self.position.is_long and not self.position.is_short:
            self.pasoUnoCompra = 1
        elif self.ema30[-1] < self.ema75[-1] and self.ema30[-1] > self.ema100[-1] and not self.position.is_short and not self.position.is_long:
            self.pasoUnoVenta = 1

        if self.pasoUnoCompra > 0 and self.ema30[-1] > self.ema100[-1] and self.ema75[-1] > self.ema100[-1]:
            if self.ema30[-1] > self.ema75[-1]:
                self.pasoDosCompra = 1
            else:
                self.pasoUnoCompra = 0
                self.pasoDosCompra = 0
        elif self.pasoUnoVenta > 0 and self.ema30[-1] < self.ema100[-1] and self.ema75[-1] < self.ema100[-1]:
            if self.ema30[-1] < self.ema75[-1]:
                self.pasoDosVenta = 1
            else:
                self.pasoUnoVenta = 0
                self.pasoDosVenta = 0

        if self.pasoUnoCompra > 0 and self.pasoDosCompra > 0 and price < self.ema100[-1] and self.ema100[-1] > self.ema200[-1]:
            self.pasoTresCompra = 1
        elif self.pasoUnoVenta > 0 and self.pasoDosVenta > 0 and price > self.ema100[-1] and self.ema100[-1] < self.ema200[-1]:
            self.pasoTresVenta = 1

        if self.pasoTresCompra > 0 and price < self.ema200[-1]:
            self.pasoUnoCompra = 0
            self.pasoDosCompra = 0
            self.pasoTresCompra = 0
        elif self.pasoTresVenta > 0 and price > self.ema200[-1]:
            self.pasoUnoVenta = 0
            self.pasoDosVenta = 0
            self.pasoTresVenta = 0

        if self.pasoTresCompra > 0 and price > self.ema75[-1]:
            self.buy(limit = None, sl = price*0.992, tp = price*1.04)
            self.pasoUnoCompra = 0
            self.pasoDosCompra = 0
            self.pasoTresCompra = 0
            self.pasoUnoVenta = 0
            self.pasoDosVenta = 0
            self.pasoTresVenta = 0
        elif self.pasoTresVenta > 0 and price < self.ema75[-1]:
            self.sell(limit = None, sl = price*1.008, tp = price*0.96)
            self.pasoUnoVenta = 0
            self.pasoDosVenta = 0
            self.pasoTresVenta = 0
            self.pasoUnoCompra = 0
            self.pasoDosCompra = 0
            self.pasoTresCompra = 0

bt = Backtest(data,EMAcross,cash = 1000000, exclusive_orders=True)

#Ejecutamos el backtest
stats = bt.run()

#Vamos los resultados del backtest

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

print(stats)
print(stats._trades)
#bt.plot(filename='backtest_plot.html', resample=False, plot_equity=False, plot_volume=False, relative_equity=False, superimpose=False, show_legend=False, open_browser=False)
