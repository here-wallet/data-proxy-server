import yaml

with open("apple-app-site-association", "r") as f:
    APPLE_APP_SITE_ASSOCIATION = f.read()

with open("apy_key", "r") as f:
    APY_KEY = f.read().replace("\n", "")


with open("config.yaml", "r") as config_file:
    CONFIG = yaml.safe_load(config_file)
