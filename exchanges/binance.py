"""
Binance (testnet/live) adapter via ccxt.
"""
import ccxt
from services.crypto import decrypt

def get_binance_api(api_key_enc, api_secret_enc, passphrase_enc=None, testnet=True):
    api_key = decrypt(api_key_enc)
    api_secret = decrypt(api_secret_enc)
    params = {"apiKey": api_key, "secret": api_secret}
    if testnet:
        b = ccxt.binance({
            "apiKey": api_key,
            "secret": api_secret,
            "options": {"defaultType": "future"},
        })
        b.set_sandbox_mode(True)
    else:
        b = ccxt.binance(params)
    return b