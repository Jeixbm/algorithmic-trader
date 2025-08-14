# ml_training/research.py
import sys
import os
import pandas as pd
import itertools

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backtester import run_backtest_engine

def run_research():
    """
    Ejecuta una optimización masiva para la estrategia de Solana.
    """
    # --- 1. Definir los rangos de parámetros a probar para SOLANA ---
    strategy_param_ranges = {
        'fast': [10, 15, 20],
        'slow': [40, 50, 60],
        'rsi_period': [14, 21],
        'rsi_threshold': [50, 55]
    }
    
    risk_param_ranges = {
        'risk_per_trade': [0.02],
        'atr_period': [14],
        'atr_multiplier': [2.5, 3.0, 3.5]
    }

    # --- 2. Cargar los datos de Solana ---
    data_filename = 'SOL_USDT_4h_data.csv'
    try:
        print(f"Cargando datos históricos desde '{data_filename}'...")
        historical_data = pd.read_csv(data_filename, index_col=0, parse_dates=True)
        print("Datos cargados exitosamente.")
    except FileNotFoundError:
        print(f"Error: No se encontró '{data_filename}'. Ejecuta 'download_binance_data.py' primero.")
        return

    # --- 3. Generar todas las combinaciones ---
    strat_keys, strat_values = zip(*strategy_param_ranges.items())
    risk_keys, risk_values = zip(*risk_param_ranges.items())
    
    strategy_combinations = [dict(zip(strat_keys, v)) for v in itertools.product(*strat_values)]
    risk_combinations = [dict(zip(risk_keys, v)) for v in itertools.product(*risk_values)]
    
    all_results = []
    run_count = 0
    total_runs = len(strategy_combinations) * len(risk_combinations)
    print(f"\nSe realizarán un total de {total_runs} backtests para Solana...")

    # --- 4. Ejecutar el backtest para cada combinación ---
    for strat_params in strategy_combinations:
        for risk_params in risk_combinations:
            run_count += 1
            print(f"\n--- Ejecutando Backtest [{run_count}/{total_runs}] ---")
            print(f"Estrategia: {strat_params} | Riesgo: {risk_params}")
            
            initial_cap, final_cap, trades_list, max_dd = run_backtest_engine(
                historical_data, 'analyze_sol_combined', strat_params, risk_params
            )
            
            # Construir el reporte a partir de los resultados
            total_trades = len(trades_list)
            if total_trades > 0:
                wins = sum(1 for t in trades_list if t['win'])
                gross_profit = sum(t['profit_usd'] for t in trades_list if t['win'])
                gross_loss = abs(sum(t['profit_usd'] for t in trades_list if not t['win']))
                report = {
                    "Capital Final": final_cap,
                    "Ganancia Neta (%)": ((final_cap - 10000) / 10000) * 100,
                    "Drawdown Máximo (%)": max_dd * 100,
                    "Total de Operaciones": total_trades,
                    "Tasa de Acierto (%)": (wins / total_trades) * 100,
                    "Factor de Beneficio": gross_profit / gross_loss if gross_loss > 0 else float('inf'),
                }
                full_result = {**strat_params, **risk_params, **report}
                all_results.append(full_result)

    # --- 5. Guardar y mostrar el reporte final ---
    results_df = pd.DataFrame(all_results)
    results_df.sort_values(by='Factor de Beneficio', ascending=False, inplace=True)
    
    output_file = 'solana_optimization_results.csv'
    results_df.to_csv(output_file, index=False, float_format='%.2f')
    
    print(f"\n\n✅ Investigación completada. Los resultados están en '{output_file}'")
    print("\n--- Mejores 5 Estrategias para Solana (ordenadas por Factor de Beneficio) ---")
    print(results_df.head(5).to_string())

if __name__ == "__main__":
    run_research()