import pandas as pd
import pandas_ta as ta
import numpy as np

def run_backtest(sol_6h_df, btc_6h_df, btc_1d_df, 
                 initial_capital=500.0,
                 leverage=1.0,
                 don_len=20, kc_len=20, kc_mult=1.8, 
                 ema_fast_len=50, ema_slow_len=200, 
                 adx_len=14, adx_min=20.0, 
                 risk_pct=0.0075, atr_stop_mult=2.0, tp_r_mult=1.5,
                 use_chandelier_exit=False,
                 ce_period=15,
                 ce_mult=2.5):

    # --- 1. Preparación de Datos e Indicadores ---
    btc_6h_df = btc_6h_df.add_prefix('btc_')
    btc_1d_df = btc_1d_df.add_prefix('btc_1d_')
    
    sol_6h_df['datetime'] = pd.to_datetime(sol_6h_df['datetime'])
    btc_6h_df['btc_datetime'] = pd.to_datetime(btc_6h_df['btc_datetime'])
    btc_1d_df['btc_1d_datetime'] = pd.to_datetime(btc_1d_df['btc_1d_datetime'])
    
    sol_6h_df.set_index('datetime', inplace=True)
    btc_6h_df.set_index('btc_datetime', inplace=True)
    btc_1d_df.set_index('btc_1d_datetime', inplace=True)
    
    df = sol_6h_df.join(btc_6h_df, how='inner')
    df = pd.merge_asof(df.sort_index(), btc_1d_df.sort_index(), 
                       left_index=True, right_index=True, direction='backward')
    
    df.ta.ema(length=ema_fast_len, append=True, col_names=('EMA_fast'))
    df.ta.ema(length=ema_slow_len, append=True, col_names=('EMA_slow'))
    df.ta.atr(length=14, append=True, col_names=('ATR'))
    df.ta.adx(length=adx_len, append=True, col_names=('ADX', 'DMP', 'DMN'))
    donchian = ta.donchian(high=df['high'], low=df['low'], length=don_len)
    df['DON_upper'] = donchian[f'DCU_{don_len}_{don_len}']
    df['DON_lower'] = donchian[f'DCL_{don_len}_{don_len}']
    keltner = df.ta.kc(length=kc_len, scalar=kc_mult)
    df['KC_upper'] = keltner[f'KCUe_{kc_len}_{kc_mult}']
    df['KC_lower'] = keltner[f'KCLe_{kc_len}_{kc_mult}']
    df['btc_EMA_slow_6h'] = ta.ema(df['btc_close'], length=ema_slow_len)
    df['btc_EMA_slow_1d'] = ta.ema(df['btc_1d_close'], length=200)

    ce_atr = ta.atr(df['high'], df['low'], df['close'], length=ce_period)
    highest_high = df['high'].rolling(window=ce_period).max()
    lowest_low = df['low'].rolling(window=ce_period).min()
    df['CE_long'] = highest_high - ce_atr * ce_mult
    df['CE_short'] = lowest_low + ce_atr * ce_mult
    
    btc_up = (df['btc_close'] > df['btc_EMA_slow_6h']) & (df['btc_1d_close'] > df['btc_EMA_slow_1d'])
    btc_down = (df['btc_close'] < df['btc_EMA_slow_6h']) & (df['btc_1d_close'] < df['btc_EMA_slow_1d'])
    up_trend = (df['close'] > df['EMA_slow']) & (df['EMA_fast'] > df['EMA_slow'])
    down_trend = (df['close'] < df['EMA_slow']) & (df['EMA_fast'] < df['EMA_slow'])
    anti_chop = df['ADX'] >= adx_min
    long_break = up_trend & anti_chop & (df['close'] > df['DON_upper'].shift(1)) & (df['close'] > df['KC_upper'])
    short_break = down_trend & anti_chop & (df['close'] < df['DON_lower'].shift(1)) & (df['close'] < df['KC_lower'])
    df['signal_long'] = long_break & btc_up
    df['signal_short'] = short_break & btc_down

    # --- 3. Bucle de Simulación de Trading ---
    trades = []
    equity = initial_capital
    in_position = False
    position_type = None
    entry_price = 0; entry_time = None
    stop_loss = 0; take_profit_1 = 0
    position_size_coins = 0; partial_tp_hit = False
    equity_curve = [initial_capital]

    for i, row in df.iterrows():
        if in_position:
            exit_condition = False
            if use_chandelier_exit:
                if (position_type == 'long' and row['close'] < row['CE_long']) or \
                   (position_type == 'short' and row['close'] > row['CE_short']):
                    exit_condition = True
            else:
                if (position_type == 'long' and row['close'] < row['EMA_fast']) or \
                   (position_type == 'short' and row['close'] > row['EMA_fast']):
                    exit_condition = True

            equity_changed_in_step = False
            if (position_type == 'long' and row['low'] <= stop_loss) or (position_type == 'short' and row['high'] >= stop_loss):
                exit_price = stop_loss
                pnl = ((exit_price - entry_price) * position_size_coins if position_type == 'long' else (entry_price - exit_price) * position_size_coins) * leverage
                equity += pnl
                trades.append({'entry_date': entry_time, 'exit_date': i, 'type': position_type, 'entry_price': entry_price, 'exit_price': exit_price, 'pnl': pnl, 'size': position_size_coins})
                in_position = False; equity_changed_in_step = True
            elif exit_condition:
                exit_price = row['close']
                pnl = ((exit_price - entry_price) * position_size_coins if position_type == 'long' else (entry_price - exit_price) * position_size_coins) * leverage
                equity += pnl
                trades.append({'entry_date': entry_time, 'exit_date': i, 'type': position_type, 'entry_price': entry_price, 'exit_price': exit_price, 'pnl': pnl, 'size': position_size_coins})
                in_position = False; equity_changed_in_step = True
            elif not partial_tp_hit and ((position_type == 'long' and row['high'] >= take_profit_1) or (position_type == 'short' and row['low'] <= take_profit_1)):
                partial_exit_price = take_profit_1
                partial_size = position_size_coins / 2
                pnl = ((partial_exit_price - entry_price) * partial_size if position_type == 'long' else (entry_price - partial_exit_price) * partial_size) * leverage
                equity += pnl
                trades.append({'entry_date': entry_time, 'exit_date': i, 'type': f"partial_{position_type}", 'entry_price': entry_price, 'exit_price': partial_exit_price, 'pnl': pnl, 'size': partial_size})
                position_size_coins /= 2; stop_loss = entry_price; partial_tp_hit = True; equity_changed_in_step = True
            
            if equity_changed_in_step:
                equity_curve.append(equity)
        
        if not in_position:
            if row['signal_long']:
                entry_price, entry_time = row['close'], i
                risk_per_coin = entry_price - (entry_price - row['ATR'] * atr_stop_mult)
                if risk_per_coin <= 0: continue
                position_size_usd = equity * risk_pct
                position_size_coins = position_size_usd / risk_per_coin
                stop_loss = entry_price - risk_per_coin
                take_profit_1 = entry_price + (risk_per_coin * tp_r_mult)
                in_position, position_type, partial_tp_hit = True, 'long', False
            elif row['signal_short']:
                entry_price, entry_time = row['close'], i
                risk_per_coin = (entry_price + row['ATR'] * atr_stop_mult) - entry_price
                if risk_per_coin <= 0: continue
                position_size_usd = equity * risk_pct
                position_size_coins = position_size_usd / risk_per_coin
                stop_loss = entry_price + risk_per_coin
                take_profit_1 = entry_price - (risk_per_coin * tp_r_mult)
                in_position, position_type, partial_tp_hit = True, 'short', False
    
    # --- 4. Análisis de Resultados ---
    if not trades: return None, None
    trades_df = pd.DataFrame(trades)
    equity_series = pd.Series(equity_curve)
    running_max = equity_series.cummax()
    drawdown = running_max - equity_series
    max_drawdown = drawdown.max()
    max_drawdown_pct = (max_drawdown / running_max.max()) * 100 if running_max.max() > 0 else 0
    wins = trades_df[trades_df['pnl'] > 0]
    losses = trades_df[trades_df['pnl'] <= 0]
    total_trades = len(trades_df)
    win_rate = len(wins) / total_trades if total_trades > 0 else 0
    gross_profit = wins['pnl'].sum()
    gross_loss = abs(losses['pnl'].sum())
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf
    net_profit = trades_df['pnl'].sum()
    
    results = {
        "net_profit": f"${net_profit:,.2f}", 
        "max_drawdown": f"${max_drawdown:,.2f} ({max_drawdown_pct:.2f}%)",
        "profit_factor": f"{profit_factor:.2f}", 
        "total_trades": total_trades, 
        "win_rate": f"{win_rate:.2%}"
    }
    return results, trades_df

if __name__ == '__main__':
    try:
        sol_df_orig = pd.read_csv('data/SOL_USDT_6h.csv')
        btc_6h_df_orig = pd.read_csv('data/BTC_USDT_6h.csv')
        btc_1d_df_orig = pd.read_csv('data/BTC_USDT_1d.csv')

        base_params = {
            'adx_min': 18,
            'kc_mult': 1.8,
            'atr_stop_mult': 2.0
        }
        
        print("--- Comparando Estrategias de Salida (con Apalancamiento 5x) ---")

        print("\n--- Método Original: Salida por Cruce de EMA ---")
        results_ema, _ = run_backtest(
            sol_df_orig.copy(), btc_6h_df_orig.copy(), btc_1d_df_orig.copy(),
            leverage=5.0,
            use_chandelier_exit=False,
            **base_params
        )
        if results_ema:
            print(results_ema)

        print("\n--- Método Nuevo: Salida por Chandelier Exit ---")
        results_ce, _ = run_backtest(
            sol_df_orig.copy(), btc_6h_df_orig.copy(), btc_1d_df_orig.copy(),
            leverage=5.0,
            use_chandelier_exit=True,
            **base_params
        )
        if results_ce:
            print(results_ce)

    except Exception as e:
        print(f"Ocurrió un error: {e}")
        import traceback
        traceback.print_exc()