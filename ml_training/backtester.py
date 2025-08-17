# ml_training/backtester.py
import sys
import os
import pandas as pd
import pandas_ta as ta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from strategy import Strategy
from risk_manager import RiskManager

def run_backtest_engine(historical_data, strategy_func_name, strategy_params, risk_params, initial_capital=10000, verbose=True):
    strategy = Strategy(verbose=False, **strategy_params)
    strategy_func = getattr(strategy, strategy_func_name)
    risk_manager = RiskManager(default_risk_per_trade=risk_params['risk_per_trade'], verbose=False)

    capital, position, trades, peak_capital, max_drawdown = initial_capital, None, [], initial_capital, 0
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
                if verbose:
                    print(f"{latest_candle.name.date()}: VENTA a ${exit_price:,.2f} | P/L: ${profit_or_loss:,.2f} | Capital: ${capital:,.2f}")
                position = None

        if not position and signal == 'BUY':
            entry_price = latest_candle['close']
            stop_loss_price = entry_price - (latest_candle[atr_col_name] * risk_params['atr_multiplier'])
            position_size_usd = risk_manager.calculate_position_size(capital, entry_price, stop_loss_price)
            if position_size_usd and position_size_usd > 0:
                amount_of_asset = position_size_usd / entry_price
                position = {'entry_price': entry_price, 'trailing_stop_loss': stop_loss_price, 'amount_of_asset': amount_of_asset}
                if verbose:
                    print(f"{latest_candle.name.date()}: COMPRA a ${entry_price:,.2f} | Tamaño: ${position_size_usd:,.2f}")

        peak_capital = max(peak_capital, capital)
        drawdown = (peak_capital - capital) / peak_capital
        max_drawdown = max(max_drawdown, drawdown)

    return initial_capital, capital, trades, max_drawdown

def build_report(initial_capital, final_capital, trades, max_drawdown, historical_data):
    # (El cuerpo de esta función no necesita cambios)
    pass

def print_professional_report(report, initial_capital=10000):
    # (El cuerpo de esta función no necesita cambios)
    pass

if __name__ == "__main__":
    # --- CAMBIO CLAVE: Cargar los datos de 6 horas de Solana ---
    data_filename = 'SOL_USDT_6h_data.csv'
    try:
        historical_data = pd.read_csv(data_filename, index_col=0, parse_dates=True)
    except FileNotFoundError:
        print(f"Error: No se encontró '{data_filename}'. Ejecuta el script de descarga para 6h primero.")
        sys.exit()

    # Parámetros base para la nueva estrategia VWAP Pullback
    strategy_params = {
        'emaFastLen': 20,
        'emaMidLen': 50,
        'emaSlowLen': 200,
        'rsiLen': 14
    }
    risk_params = {'risk_per_trade': 0.01, 'atr_period': 14, 'atr_multiplier': 1.5}

    initial_cap, final_cap, trades_list, max_dd = run_backtest_engine(
        historical_data, 
        'analyze_sol_vwap_pullback', # Apuntando a la nueva estrategia
        strategy_params, 
        risk_params,
        verbose=True
    )
    
    # (Asegúrate de que tus funciones de reporte estén completas aquí)
    report = build_report(initial_cap, final_cap, trades_list, max_dd, historical_data)
    print_professional_report(report, initial_capital=initial_cap)