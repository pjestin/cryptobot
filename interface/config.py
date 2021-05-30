import json


class Config:
    CONFIG_FILE = "config.json"

    class Profile:
        def __init__(self, profile_data):
            self.symbol = profile_data["symbol"]
            self.quantity = profile_data["quantity"]

    def __init__(self):
        with open(self.CONFIG_FILE, newline="") as file:
            config_data = json.load(file)
            self.interval = config_data["interval"]
            self.period = config_data["period"]
            self.profiles = {
                symbol: self.Profile(profile_data)
                for symbol, profile_data in config_data["profiles"].items()
            }

    def profile_config(self, symbol):
        if symbol not in self.profiles:
            raise EnvironmentError("Profile name does not exist")
        return self.profiles[symbol]
