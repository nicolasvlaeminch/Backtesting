import backtrader as bt
import pandas as pd

# Descargar los datos y cargarlos en un DataFrame
data = pd.read_csv("BTC-2017-2M.csv")
data["Date"] = pd.to_datetime(data["Date"])
data = data.set_index("Date")

class EMACrossStrategy(bt.Strategy):
    params = (
        ("ema_short", 50),
        ("ema_long", 200)
    )

    def __init__(self):
        self.ema_short = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=self.params.ema_short)
        self.ema_long = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=self.params.ema_long)

    def next(self):
        if self.ema_short > self.ema_long and not self.position:
            self.buy()
        elif self.ema_short < self.ema_long and self.position:
            self.sell()

cerebro = bt.Cerebro()

# Agregar la estrategia
cerebro.addstrategy(EMACrossStrategy)

# Agregar los datos de entrada
data_feed = bt.feeds.PandasData(dataname=data)
cerebro.adddata(data_feed)

# Configurar el capital inicial
cerebro.broker.set_cash(100000)

# Ejecutar el backtest
cerebro.run()

# Mostrar el gráfico de resultados
cerebro.plot(style='candlestick')
