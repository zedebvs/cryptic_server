from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES


def encrypt_AES_256_ECB(key):
    
    plaintext = get_random_bytes(32)
    
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = cipher.encrypt(plaintext)
    
    return ciphertext.hex()

def decrypt_AES_256_ECB(key, ciphertext):
    
    cipher = AES.new(key, AES.MODE_ECB)
    text = cipher.decrypt(ciphertext)
    
    return text.hex()
