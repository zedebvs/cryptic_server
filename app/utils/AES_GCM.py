from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

TAG_LENGTH_BITS = 128
IV_LENGTH_BYTES = 12

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def encrypt(plaintext, hex_key):
    key = hex_to_bytes(hex_key)
    iv = get_random_bytes(IV_LENGTH_BYTES)

    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))

 
    return (
        b64encode(ciphertext).decode('utf-8'),
        b64encode(iv).decode('utf-8'),
        b64encode(tag).decode('utf-8')
    )

def decrypt(ciphertext_b64, iv_b64, tag_b64, hex_key):
    try:
        key = hex_to_bytes(hex_key)
        iv = b64decode(iv_b64)
        ciphertext = b64decode(ciphertext_b64)
        tag = b64decode(tag_b64)

        cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
        plaintext_bytes = cipher.decrypt_and_verify(ciphertext, tag)
    except Exception as e:
        print(f"Ошибка в ГСМ: {e}")
    return plaintext_bytes.decode('utf-8')
