import configparser

config = configparser.ConfigParser()

config.read("config.conf")

# Telegram API Configuration
API_ID = config['API']['API_ID']
API_HASH = config['API']['API_HASH']
PHONE = config['API']['PHONE']

# Channel to analyze
CHANNEL_USERNAME = config['CHANNEL']['CHANNEL_USERNAME']  # Can be @username or channel ID

# Data collection interval (in seconds)
COLLECTION_INTERVAL = 3600  # 1 hour

# Database
DATABASE_PATH = 'analytics.db'
