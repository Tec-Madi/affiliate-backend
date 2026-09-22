from dotenv import load_dotenv
import os

load_dotenv(".env", override=True)

############## DATABASE URLS #################
AISHORASUB_DATABASE_URL = os.getenv("AISHORASUB_DATABASE_URL")
MEERALINKS_DATABASE_URL = os.getenv("MEERALINKS_DATABASE_URL")
HZQUICKLINK_DATABASE_URL = os.getenv("HZQUICKLINK_DATABASE_URL")

############## ENCRYPTION KEY ################
ENCRYPTION_SECRET_KEY = os.getenv('ENCRYPTION_KEY').encode()

############## SECRET KEYS ##################
SECRET_KEY = os.getenv('SECRET_KEY')

ALGORITHMS_KEY = os.getenv('ALGORITHMS_KEY')

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))

################ EMAIL ###############
RESEND_API_KEY = os.getenv("RESEND_API_KEY")