# trading_bot/strategy.py
import pandas as pd
import pandas_ta as ta

class Strategy:
    """
    Versión 6: Contiene múltiples estrategias para múltiples activos.
    """
    def __init__(self, **params):
        """
        Inicializa la estrategia con un diccionario de parámetros flexible.
        """
        # Asignar parámetros dinámicamente
        self.params = params
        # No ponemos logs para no saturar la consola en pruebas masivas

    def analyze_btc_trend_rider(self, data):
        """Estrategia de Cruce de EMAs para BTC."""
        fast_period = self.params.get('fast', 20)
        slow_period = self.params.get('slow', 50)
        trend_period = self.params.get('trend', 200)

        ema_fast = data.ta.ema(length=fast_period)
        ema_slow = data.ta.ema(length=slow_period)
        ema_trend = data.ta.ema(length=trend_period)

        if ema_fast is None or ema_slow is None or ema_trend is None: return 'HOLD'
            
        ema_diff = ema_fast - ema_slow
        
        latest_close = data['close'].iloc[-1]
        latest_trend_ema = ema_trend.iloc[-1]
        latest_diff = ema_diff.iloc[-1]
        previous_diff = ema_diff.iloc[-2]

        is_uptrend = latest_close > latest_trend_ema
        buy_signal = previous_diff <= 0 and latest_diff > 0
        sell_signal = previous_diff >= 0 and latest_diff < 0

        if is_uptrend and buy_signal: return 'BUY'
        if sell_signal: return 'SELL'
        return 'HOLD'
        
    def analyze_sol_combined(self, data):
        """
        Nueva estrategia para SOL: Cruce de EMAs + Filtro de Momentum RSI.
        """
        fast_period = self.params.get('fast', 20)
        slow_period = self.params.get('slow', 50)
        rsi_period = self.params.get('rsi_period', 14)
        rsi_threshold = self.params.get('rsi_threshold', 50)

        # Calcular indicadores
        ema_fast = data.ta.ema(length=fast_period)
        ema_slow = data.ta.ema(length=slow_period)
        rsi = data.ta.rsi(length=rsi_period)

        if ema_fast is None or ema_slow is None or rsi is None: return 'HOLD'
            
        # Lógica de Cruce
        ema_diff = ema_fast - ema_slow
        latest_diff = ema_diff.iloc[-1]
        previous_diff = ema_diff.iloc[-2]
        
        # Lógica de RSI
        latest_rsi = rsi.iloc[-1]
        
        # Condiciones
        buy_crossover = previous_diff <= 0 and latest_diff > 0
        sell_crossover = previous_diff >= 0 and latest_diff < 0
        momentum_confirmed = latest_rsi > rsi_threshold

        if buy_crossover and momentum_confirmed: return 'BUY'
        if sell_crossover: return 'SELL'
        return 'HOLD'