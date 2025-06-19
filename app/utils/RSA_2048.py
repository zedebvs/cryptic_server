from app.data_base.db_setup import SessionLocal
from app.data_base.models import UserKeyAES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from app.utils.AES_256 import decrypt_AES_256_ECB, encrypt_AES_256_ECB
from app.config import AES_KEY_1
from fastapi import HTTPException
import base64
from app.models.model import AesChipherKey
from Crypto.Hash import SHA256, SHA1
from Crypto.Cipher import PKCS1_v1_5 #pkcs1_15

def RSA_encrypt(User_id, public_key_bytes):
    with SessionLocal() as db:
        try:
            for_encrypt = db.query(UserKeyAES).filter(UserKeyAES.id == User_id).first()
            if not for_encrypt:
                
                key_encrypt = encrypt_AES_256_ECB(AES_KEY_1)
                
                user_key_entry = UserKeyAES(id=User_id, key_aes=key_encrypt)
                db.add(user_key_entry)
                db.commit()
                
                key_for_encrypt = decrypt_AES_256_ECB(AES_KEY_1, bytes.fromhex(key_encrypt))
            else:
                
                key_encrypt = for_encrypt.key_aes
                key_encrypt = bytes.fromhex(key_encrypt)
                key_for_encrypt = decrypt_AES_256_ECB(AES_KEY_1, key_encrypt)

            key_for_encrypt_bytes = bytes.fromhex(key_for_encrypt)
            public_key = RSA.import_key(public_key_bytes)
            print(public_key)
            cipher_rsa = PKCS1_v1_5.new(public_key) #, hashAlgo=SHA1) # , hashAlgo=SHA1) #, mgfunc=lambda x, y: PKCS1_OAEP.MGF1(x, SHA1)) #, mgfunc=lambda x, y: PKCS1_OAEP.MGF1(x, SHA256))
            encrypted_aes_key = cipher_rsa.encrypt(key_for_encrypt_bytes)
            
            encrypted_base64 = base64.b64encode(encrypted_aes_key).decode()
            
            return AesChipherKey(key=encrypted_base64)
        
        except Exception as e:
            raise HTTPException(status_code=402, detail="error")
