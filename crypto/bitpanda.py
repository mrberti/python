#%%
import os
import json
import gzip
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import pandas as pd

FILE_BASE_PATH = os.path.dirname(__file__)
API_KEY_FILE_PATH = os.path.join(FILE_BASE_PATH, "api_keys.json")

USER_AGENT = "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
HEADERS_BASE = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json",
}

class Bitpanda():
    def __init__(self, api_key_file=None):
        self.eur_balance = 0.
        self.ticker_data = {}
        self.crypto_wallets_data = []
        self.asset_wallets_data = []
        self.metal_wallets_data = []
        self.index_wallets_data = []
        self.fiat_wallets_data = []
        self.all_wallets_data = []
        self.simplified_wallets = {}
        self.crypto_ids = {}
        self.headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-API-KEY": "",
        }
        self.api_key = self.get_api_key(api_key_file)

    def get_api_key(self, api_key_file=None):
        if not api_key_file:
            api_key_file = API_KEY_FILE_PATH
        with open(api_key_file, "r") as f:
            api_key_json = json.load(f)
            self.api_key = api_key_json["bitpanda"]["api_key"]
        self.headers["X-API-KEY"] = self.api_key
        return self.api_key

    def get_api(self, request):
        request_uri = "https://api.bitpanda.com/v1/{}".format(request)
        req = Request(request_uri, headers=self.headers)
        response = urlopen(req, timeout=5.)
        raw_data = response.read()
        print(f"<<< {request_uri}")
        print(f">>> Received data size: {len(raw_data)}")
        encoding = response.headers.get("content-encoding")
        if encoding:
            if "gzip" in encoding:
                raw_data = gzip.decompress(raw_data)
        data = json.loads(raw_data.decode("utf8"))
        return data

    def update_ticker(self):
        self.ticker_data = self.get_api("ticker")
        return self.ticker_data

    def update_crypto_wallets(self):
        self.crypto_wallets_data = self.get_api("wallets")["data"]
        return self.crypto_wallets_data

    def update_asset_wallets(self):
        self.asset_wallets_data = self.get_api("asset-wallets")["data"]
        self.metal_wallets_data = self.asset_wallets_data["attributes"]["commodity"]["metal"]["attributes"]["wallets"]
        self.index_wallets_data = self.asset_wallets_data["attributes"]["index"]["index"]["attributes"]["wallets"]
        return self.asset_wallets_data

    def update_fiat_wallets(self):
        self.fiat_wallets_data = self.get_api("fiatwallets")["data"]
        return self.fiat_wallets_data

    def update_all_wallets(self):
        self.update_crypto_wallets()
        self.update_asset_wallets()
        self.update_fiat_wallets()
        self.all_wallets_data = (
            self.crypto_wallets_data
            + self.metal_wallets_data
            + self.index_wallets_data
            + self.fiat_wallets_data)
        return self.all_wallets_data

    def get_all_non_empty_wallets(self, update=True):
        if update:
            self.update_all_wallets()
        non_empty_wallets = []
        for wallet in self.all_wallets_data:
            balance = float(wallet["attributes"]["balance"])
            if balance > 0.:
                non_empty_wallets.append(wallet)
        return non_empty_wallets

    def get_price(self, symbol_crypto, symbol_fiat, update=True):
        if update:
            self.update_ticker()
        try:
            return float(self.ticker_data.get(
                symbol_crypto.upper()).get(symbol_fiat.upper()))
        except AttributeError:
            return 0.

    def get_crypto_ids(self, update=True):
        if update or not self.crypto_ids:
            self.update_crypto_wallets()
        crypto_ids = {}
        for wallet in self.crypto_wallets_data:
            cryptocoin_id = wallet["attributes"]["cryptocoin_id"]
            cryptocoin_symbol = wallet["attributes"]["cryptocoin_symbol"]
            crypto_ids[cryptocoin_id] = cryptocoin_symbol
        self.crypto_ids = crypto_ids
        return crypto_ids

    def simplify_wallets(self, update=True):
        self.simplified_wallets = {}
        if update:
            self.update_all_wallets()
        for wallet in self.all_wallets_data:
            wallet_attributes = wallet["attributes"]
            if "cryptocoin_symbol" in wallet_attributes:
                asset_name = wallet_attributes["cryptocoin_symbol"]
            elif "fiat_symbol" in wallet_attributes:
                asset_name = wallet_attributes["fiat_symbol"]
            balance = float(wallet_attributes["balance"])
            if balance > 0:
                if asset_name in self.simplified_wallets:
                    self.simplified_wallets[asset_name] += balance
                else:
                    self.simplified_wallets[asset_name] = balance
        return self.simplified_wallets

    def calculate_eur_balance(self, update=True):
        if update:
            self.update_ticker()
            self.simplify_wallets(update=update)
        self.eur_balance = 0.
        for asset, balance in self.simplified_wallets.items():
            if asset != "EUR":
                eur_balance = balance * self.get_price(asset, "EUR", update=False)
            elif asset == "EUR":
                eur_balance = balance
            else:
                raise Exception("Unsupported asset: {}".format(asset))
            self.eur_balance += eur_balance
        return self.eur_balance

if __name__ == "__main__":
    bp = Bitpanda()
    bp.update_ticker()
    print(bp.simplify_wallets())
    print(f"{bp.calculate_eur_balance(update=False):.2f} EUR")
