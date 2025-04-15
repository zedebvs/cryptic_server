import re

def valid_username(name):
    return re.fullmatch(r'^[a-zA-Z0-9_-]{3,20}$', name)

def valid_email(email):
    return re.fullmatch(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email)

