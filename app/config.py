import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

DATABASE_URL = os.getenv("DATABASE_URL")

aes_key_1 = os.getenv("AES_1") ##
AES_KEY_1 = bytes.fromhex(aes_key_1)

aes_key_2 = os.getenv("AES_2") ##
AES_KEY_2 = bytes.fromhex(aes_key_2)
