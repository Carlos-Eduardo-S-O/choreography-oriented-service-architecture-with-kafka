import base64
import jwt
import datetime
import urllib.request as request
import json
import random
import string
import hashlib
from faker import Faker 
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from faker.providers import internet
from urllib.parse import urlencode

faker = Faker(['pt_BR'])
faker.add_provider(internet)

AUTHENTICATION_ROUTE = "http://172.18.0.6:5000/"
INFO                 = "info"
EXECUTE              = "execute"
TOKEN_KEY            = "secret_key"
PUBLIC_KEY           = "-----BEGIN PUBLIC KEY-----\nMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAt0seI15IbBvlOEP6yO4V\naUZTldEOc5aMUxqeDC5Hx4PY4B4J8A77E0sObamj+2YCHBNDH5kA1UBTl+soDNdT\nBSx0yf7SiRvsFnz4Jo1LZUo1RvqAOftrPVdNM3Xop32VFE+OPRjsReERwBRnCYvH\naGzSI+5RhPqVx1Wu1K9TvqF5OlSqS7ehWfO4F1wxQiIh6KaAb2sKUvUO38ESVVdn\n0WHKU1S0+uRil+y0JxV1EOebsEKtf1gf2gu77sc7NBytmpYR4A20Opi6Y/UUwo0d\ngI951CQQ8FftQ1MwoXL5AEHEH7Mfsr5+IrX277Jrs0Dn5HzSon3j5wgSbBdydkD2\nA1zZCsWDs9NTC9RS9VZnArj0DDcOfuUQXSclRXdhaueDeHksWFrPu5+Qp3Cnna7t\nmeS7AQdVcmHs65MBTYZ49VVWRtq/yDNxu9Bg+ZMnnREXN+5l3+I0Z/8a5XZj8wS0\nQsAuhCEiqQ5z2tCHymuX6ClHmur3ahH/R5+4DOertJX8XfwL9d9iGnhMeS+LUXF4\nBKqjPNUL1K14Wb970pGCv0dm1VUqPwRkFv6WwCua7/IC+X9KqsR7Ln8TcYgmfWFp\n+H45I++U/9RbvxmMY8MTM/8ee4GLai3ABJUT6bbdYSmorefJR3/VaMCLSUovDbaI\ndegqK9HoM9PkSQg9rB2tUiMCAwEAAQ==\n-----END PUBLIC KEY-----"
CLIENT_VERSION       = "1.0.0"

def encrypt(plaintext):
    error = None
    encrypted = ""

    try:
        # Load public key
        public_key = RSA.importKey(PUBLIC_KEY)
        cipher = PKCS1_v1_5.new(public_key)

        encrypted = plaintext.encode('utf-8')
        encrypted = cipher.encrypt(encrypted)
        encrypted = base64.b64encode(encrypted)
        encrypted = encrypted.decode('utf-8')
    except Exception as e:
        error = "ERROR_UNABLE_TO_COMPLETE: " + str(e)

    return error, encrypted

def get_service_info():
    url = AUTHENTICATION_ROUTE + INFO

    return access_url(url)

def get_key():
    return TOKEN_KEY

def access_url(url):
    response = request.urlopen(url)
    data = response.read()
    
    return data.decode("utf-8")

def generate_user():
    ID = "".join(random.choice(string.ascii_letters + string.punctuation) for _ in range(12))
    
    ID = hashlib.sha256(ID.encode("utf-8")).hexdigest()
    
    user = {
        "id": ID,
        "name": faker.name(),
        "age": random.randint(0,120)
    }
    
    return user

def generate_valid_token():
    user = generate_user()
    
    token = jwt.encode({"user": user, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=5000)}, get_key(), algorithm="HS256")
            
    return token.decode("utf-8")

def generate_fake_token():
    user = generate_user()
    
    token = jwt.encode({"user": user, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=5000)}, "fake key", algorithm="HS256")
    
    return token.decode("utf-8")

def generate_valid_header():
    ip = faker.ipv4_private()
    author = faker.name()
    version =  str(random.randint(3, 5)) + "." + str(random.randint(1, 9)) + "." + str(random.randint(1, 9))
    device = random.choice(["mobile", "desktop"])
    location = random.choice(["América", "Europa", "África", "Ásia", "Oceania", "Antártida"])
    
    hearder = {
        "ip": ip,
        "author": author,
        "api": version,
        "device": device,
        "location": location
    }
    
    return hearder

def generate_fake_header():
    hearder = {
        "ip": "",
        "author": "",
        "api": "",
        "device": "",
        "location": ""
    }
    
    return hearder

def prepare_data(header, token):
    data =  json.dumps({
        "header": header,
        "token": token
    })
    
    return data

def encode_data(data):
    error, encrypted_data =  encrypt(data)
    
    encoded_data = urlencode({"data": encrypted_data})
    
    return error, encoded_data

def get_url_with_no_problem():
    header = generate_valid_header()
    token = generate_valid_token()
    
    data = prepare_data(header, token)
    
    error, encoded_data =  encode_data(data)
    
    if not error:
        url = AUTHENTICATION_ROUTE + EXECUTE + "?" + encoded_data
    return url

def get_url_with_criptografy_problem():
    url = None
    header = generate_valid_header()
    token = generate_valid_token()

    data = prepare_data(header, token)
    
    url = AUTHENTICATION_ROUTE + EXECUTE + "?" + urlencode({"data": data})
    
    return url

def get_url_with_token_problem():
    url = None
    header = generate_valid_header()
    token  = generate_fake_token()
    
    data = prepare_data(header, token)
    
    error, encoded_data =  encode_data(data)
    
    if not error:
        url = AUTHENTICATION_ROUTE + EXECUTE + "?" + encoded_data
    return url

def get_url_with_header_problem():
    url = None
    header = generate_fake_header()
    token  = generate_valid_token()
    
    data = prepare_data(header, token)
    
    error, encoded_data =  encode_data(data)
    
    if not error:
        url = AUTHENTICATION_ROUTE + EXECUTE + "?" + encoded_data
    return url

def get_url_to_security_verification(error):
    url = None

    if error == "":
        url = get_url_with_no_problem()
    else:
        switch = {
            "c": get_url_with_criptografy_problem(),
            "h": get_url_with_header_problem(),
            "t": get_url_with_token_problem()
        }
        
        url = switch.get(error, "Error getting url, you just use a wrong option, try:\nt for tokens, h for headers, c for cryptography errors and a empty str for not error")
    
    return url

def send_message(url):
    return access_url(url)
