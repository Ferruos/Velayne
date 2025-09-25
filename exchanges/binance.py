import ccxt

def get_exchange(api_key, api_secret, sandbox=False):
    ex = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
    })
    if sandbox:
        ex.set_sandbox_mode(True)
    return ex

def place_order(api_key, api_secret, symbol, side, amount, price=None, sandbox=False):
    ex = get_exchange(api_key, api_secret, sandbox)
    params = {"type": "LIMIT" if price else "MARKET"}
    order = ex.create_order(symbol, params["type"], side.upper(), amount, price)
    return order

def check_api_key(api_key, api_secret, sandbox=False):
    try:
        ex = get_exchange(api_key, api_secret, sandbox)
        ex.fetch_balance()
        return True
    except Exception:
        return False