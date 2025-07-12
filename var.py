from dotenv import load_dotenv
import os 
import logging
from logging.handlers import RotatingFileHandler
import pytz

load_dotenv('config.env' , override=True)

# REQUIRED
BOT_TOKEN = os.environ.get('BOT_TOKEN','')
API_ID = os.environ.get('API_ID','')
API_HASH = os.environ.get('API_HASH' ,'')
CHANNEL_ID = int(os.environ.get("CHANNEL_ID" , ''))
OWNER = [int(x) for x in os.environ.get('OWNER' , '').split()]
ADMINS = [int(x) for x in os.environ.get('ADMINS' , '').split()]
DB_URL = os.environ.get('DB_URL' , '')
DB_NAME = os.environ.get('DB_NAME' , 'filestore')

# TOKEN SYSTEM
SHORTENER = os.environ.get('SHORTENER','False').lower() == 'true'
SHORTENER_API = os.environ.get('SHORTENER_API' , '')
SHORTENER_SITE = os.environ.get('SHORTENER_SITE' , '')
SHORTENER_PREMIUM = os.environ.get('SHORTENER_PREMIUM','False').lower() == 'true'
HOW_TO_DOWNLOAD = os.environ.get('HOW_TO_DOWNLOAD' , '')

# DOMAIN
DOMAIN = os.environ.get('DOMAIN' , '')

# DEFAULT
PORT = "8080"
AUTO_DELETE = int(os.environ.get("AUTO_DELETE",'0') or 0)
PROTECT = os.environ.get('PROTECT','False').lower() == 'true'
CHANNEL_BUTTON = os.environ.get('CHANNEL_BUTTON','True').lower() == 'true'
CUSTOM_CAPTION = os.environ.get('CUSTOM_CAPTION','')

# NORMAL FSUB
FSUB = [int(x) for x in os.environ.get('FSUB','').split()]
FSUB_LINKS = [x for x in os.environ.get('FSUB_LINKS','').split()]
FSUB_TIMEOUT = int(os.environ.get('FSUB_TIMEOUT' , '0') or 0)

# REQUEST FSUB
TOGGLE = os.environ.get('TOGGLE','False').lower() == 'true'
REQUEST_FSUB = [int(x) for x in os.environ.get('REQUEST_FSUB','').split()]
REQUEST_LINKS = [x for x in os.environ.get('REQUEST_LINKS','').split()]

# FAKE BUTTON
FAKE = [i.strip() for i in os.environ.get('FAKE' , '').split(',') if i.strip()]

# CURRENT REPO
CURRENT_REPO = os.environ.get('UPSTREAM_REPO' , '')
CURRENT_BRANCH = os.environ.get('UPSTREAM_BRANCH' , '')

#LOGGING
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            'log.txt',
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)

logging.getLogger("apscheduler").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)

if DOMAIN:
    DOMAIN = DOMAIN if DOMAIN.endswith('/') else DOMAIN + '/'

TIME_ZONE = pytz.timezone('Asia/Kolkata')
