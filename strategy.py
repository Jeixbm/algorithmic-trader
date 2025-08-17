import pandas as pd
import pandas_ta as ta
import numpy as np
from logger import log # Importar el logger para el warning

def check_strategy_6h_breakout(sol_df, btc_6h_df, btc_1d_df, config_obj):
    params = config_obj.STRATEGY_CONFIG
    
    sol_df['datetime'] = pd.to_datetime(sol_df['datetime'])
    sol_df.set_index('datetime', inplace=True)
    
    btc_6h_df['datetime'] = pd.to_datetime(btc_6h_df['datetime'])
    btc_6h_df.set_index('datetime', inplace=True)
    
    btc_1d_df['datetime'] = pd.to_datetime(btc_1d_df['datetime'])
    btc_1d_df.set_index('datetime', inplace=True)

    btc_6h_df = btc_6h_df.add_suffix('_btc_6h')
    btc_1d_df = btc_1d_df.add_suffix('_btc_1d')

    df = sol_df.join(btc_6h_df, how='inner')
    df = pd.merge_asof(
        df.sort_index(), 
        btc_1d_df.sort_index(),
        left_index=True,
        right_index=True,
        direction='backward'
    )
    
    df.ta.ema(length=params['ema_fast_len'], append=True, col_names=('EMA_fast'))
    df.ta.ema(length=params['ema_slow_len'], append=True, col_names=('EMA_slow'))
    df.ta.adx(length=params['adx_len'], append=True, col_names=('ADX', 'DMP', 'DMN'))
    
    donchian = ta.donchian(high=df['high'], low=df['low'], length=params['don_len'])
    df['DON_upper'] = donchian[f'DCU_{params["don_len"]}_{params["don_len"]}']
    df['DON_lower'] = donchian[f'DCL_{params["don_len"]}_{params["don_len"]}']
    
    keltner = ta.kc(high=df['high'], low=df['low'], close=df['close'], length=params['kc_len'], scalar=params['kc_mult'])
    df['KC_upper'] = keltner[f'KCUe_{params["kc_len"]}_{params["kc_mult"]}']
    df['KC_lower'] = keltner[f'KCLe_{params["kc_len"]}_{params["kc_mult"]}']
    
    df['btc_EMA_slow_6h'] = ta.ema(df['close_btc_6h'], length=params['ema_slow_len'])
    df['btc_EMA_slow_1d'] = ta.ema(df['close_btc_1d'], length=200)

    latest = df.iloc[-1]
    previous = df.iloc[-2]

    required_cols = ['close_btc_6h', 'btc_EMA_slow_6h', 'close_btc_1d', 'btc_EMA_slow_1d', 'EMA_slow', 'EMA_fast', 'ADX', 'DON_upper', 'DON_lower', 'KC_upper', 'KC_lower']
    
    # --- CORRECCIÓN: Usar pd.isna() en lugar de np.isnan() ---
    if any(pd.isna(latest[col]) for col in required_cols):
        log.warning("Datos insuficientes para calcular todos los indicadores. Omitiendo ciclo.")
        return None

    btc_up = (latest['close_btc_6h'] > latest['btc_EMA_slow_6h']) and (latest['close_btc_1d'] > latest['btc_EMA_slow_1d'])
    btc_down = (latest['close_btc_6h'] < latest['btc_EMA_slow_6h']) and (latest['close_btc_1d'] < latest['btc_EMA_slow_1d'])
    
    up_trend = (latest['close'] > latest['EMA_slow']) and (latest['EMA_fast'] > latest['EMA_slow'])
    down_trend = (latest['close'] < latest['EMA_slow']) and (latest['EMA_fast'] < latest['EMA_slow'])
    
    anti_chop = latest['ADX'] >= params['adx_min']
    
    long_break = up_trend and anti_chop and (latest['close'] > previous['DON_upper']) and (latest['close'] > latest['KC_upper'])
    short_break = down_trend and anti_chop and (latest['close'] < previous['DON_lower']) and (latest['close'] < previous['KC_lower'])
    
    if long_break and btc_up:
        return 'long'
    
    if short_break and btc_down:
        return 'short'
        
    return None