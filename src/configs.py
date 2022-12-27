import yaml

with open("configs/apple-app-site-association", "r") as f:
    APPLE_APP_SITE_ASSOCIATION = f.read()

with open("configs/apy_key", "r") as f:
    APY_KEY = f.read().replace("\n", "")


with open("configs/config.yaml", "r") as config_file:
    CONFIG = yaml.safe_load(config_file)
