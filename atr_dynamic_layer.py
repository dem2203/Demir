def calculate_dynamic_position_size(symbol, portfolio, risk_pct, atr):
    # Position = (Risk Amount) / (ATR * Multiplier)
    risk_amount = portfolio * (risk_pct / 100)
    position_size = risk_amount / (atr * 2.0)
    return position_size
