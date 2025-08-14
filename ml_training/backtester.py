# ml_training/backtester.py
import sys
import os
import pandas as pd
import pandas_ta as ta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from strategy import Strategy
from risk_manager import RiskManager

def run_backtest_engine(historical_data, strategy_func_name, strategy_params, risk_params, initial_capital=10000):
    """
    Motor de backtesting genérico que acepta el nombre de la función de la estrategia a probar.
    """
    strategy = Strategy(**strategy_params)
    # Obtener la función de la estrategia a probar por su nombre
    strategy_func = getattr(strategy, strategy_func_name)
    
    risk_manager = RiskManager(risk_per_trade_percentage=risk_params['risk_per_trade'])
    
    capital = initial_capital
    position = None
    trades = []
    peak_capital = initial_capital
    max_drawdown = 0

    historical_data.ta.atr(append=True, length=risk_params['atr_period'])

    start_index = 200
    for i in range(start_index, len(historical_data)):
        current_data_slice = historical_data.iloc[0:i+1]
        latest_candle = current_data_slice.iloc[-1]
        atr_col_name = f'ATRr_{risk_params["atr_period"]}'
        
        if pd.isna(latest_candle[atr_col_name]): continue
        
        signal = strategy_func(current_data_slice)

        if position:
            new_trailing_stop = latest_candle['high'] - (latest_candle[atr_col_name] * risk_params['atr_multiplier'])
            if new_trailing_stop > position['trailing_stop_loss']:
                position['trailing_stop_loss'] = new_trailing_stop

            if latest_candle['low'] <= position['trailing_stop_loss'] or signal == 'SELL':
                exit_price = position['trailing_stop_loss'] if latest_candle['low'] <= position['trailing_stop_loss'] else latest_candle['close']
                profit_or_loss = (exit_price - position['entry_price']) * position['amount_of_asset']
                capital += profit_or_loss
                trades.append({'win': profit_or_loss > 0, 'profit_usd': profit_or_loss})
                position = None
        
        if not position and signal == 'BUY':
            entry_price = latest_candle['close']
            stop_loss_price = entry_price - (latest_candle[atr_col_name] * risk_params['atr_multiplier'])
            position_size_usd = risk_manager.calculate_position_size(capital, entry_price, stop_loss_price)
            if position_size_usd and position_size_usd > 0:
                amount_of_asset = position_size_usd / entry_price
                position = {'entry_price': entry_price, 'trailing_stop_loss': stop_loss_price, 'amount_of_asset': amount_of_asset}

        peak_capital = max(peak_capital, capital)
        drawdown = (peak_capital - capital) / peak_capital
        max_drawdown = max(max_drawdown, drawdown)

    # Devolvemos los resultados crudos para que la función de reporte los procese
    return initial_capital, capital, trades, max_drawdown

def print_professional_report(initial_capital, final_capital, trades, max_drawdown, historical_data):
    """
    Toma los resultados del backtest y calcula e imprime un reporte completo.
    """
    print("\n--- Reporte de Rendimiento Profesional ---")
    
    total_trades = len(trades)
    if total_trades == 0:
        print("No se realizaron operaciones.")
        return

    wins = sum(1 for trade in trades if trade['win'])
    losses = total_trades - wins
    win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
    
    gross_profit = sum(t['profit_usd'] for t in trades if t['win'])
    gross_loss = abs(sum(t['profit_usd'] for t in trades if not t['win']))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    total_profit = final_capital - initial_capital
    profit_percentage = (total_profit / initial_capital) * 100

    print(f"Periodo Analizado:      {historical_data.index.min().date()} a {historical_data.index.max().date()}")
    print("-" * 40)
    print(f"Capital Inicial:      ${initial_capital:,.2f}")
    print(f"Capital Final:        ${final_capital:,.2f}")
    print(f"Ganancia/Pérdida Neta:${total_profit:,.2f} ({profit_percentage:.2f}%)")
    print(f"Drawdown Máximo:      {max_drawdown:.2%}")
    print("-" * 40)
    print(f"Total de Operaciones: {total_trades}")
    print(f"Tasa de Acierto:      {win_rate:.2f}%")
    print(f"Factor de Beneficio:  {profit_factor:.2f}")
    print("-" * 40)

if __name__ == "__main__":
    data_filename = 'SOL_USDT_4h_data.csv'
    try:
        historical_data = pd.read_csv(data_filename, index_col=0, parse_dates=True)
    except FileNotFoundError:
        print(f"Error: No se encontró '{data_filename}'. Ejecuta el script de descarga primero.")
        sys.exit()

    strategy_params = {'fast': 20, 'slow': 50, 'rsi_period': 14, 'rsi_threshold': 50}
    risk_params = {'risk_per_trade': 0.02, 'atr_period': 14, 'atr_multiplier': 3.0}

    # Ejecutar el motor de backtesting
    initial_cap, final_cap, trades_list, max_dd = run_backtest_engine(
        historical_data, 
        'analyze_sol_combined', 
        strategy_params, 
        risk_params
    )

    # Imprimir el reporte con los resultados
    print_professional_report(initial_cap, final_cap, trades_list, max_dd, historical_data)