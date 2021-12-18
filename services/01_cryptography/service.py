from flask import Flask, jsonify, request

from kafka import KafkaClient, KafkaProducer
from kafka.errors import KafkaError

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from urllib.parse import unquote
from time import sleep

import hashlib
import random
import string
import json
import base64

service = Flask(__name__)

PROCESS = "criptografy"
DEBUG = True

DESCRIPTION = "This system verify the requests"
VERSION = "0.1"

PRIVATE_KEY = "-----BEGIN RSA PRIVATE KEY-----\n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\n-----END RSA PRIVATE KEY-----"

def start():
    client = KafkaClient(
        bootstrap_servers = ["kafka:29092"],
        api_version=(0, 10, 1)
    )
    
    client.add_topic(PROCESS)
    client.close()
    
# Load private key from key file
def load_private_key():
    private_key = None
    
    private_key = RSA.importKey(PRIVATE_KEY)
    
    return private_key

# Decrypt a string from client
def decrypt(encrypted):
    error = None
    decrypted = ""
    private_key = load_private_key()
    
    try:
        cipher = PKCS1_v1_5.new(private_key)

        encrypted = base64.b64decode(encrypted)
        decrypted = cipher.decrypt(encrypted, None)
        decrypted = str(decrypted, 'utf-8')
    except Exception as e:
        error = {"error": e}

    return error, decrypted

@service.route("/info", methods=["GET"])
def get_info():
    info = jsonify(
        description=DESCRIPTION,
        version=VERSION
    )
    
    return info

def record_message_on_kafka_service(process, value):
    response = "ok"
    
    try:
        producer = KafkaProducer(
            bootstrap_servers=["kafka:29092"],
            api_version=(0, 10, 1)
        )
        
        producer.send(topic=process, value=value)
    except KafkaError as error:
            response = f"erro: " + str(error)
    
    return response

@service.route("/execute")
def execute():
    response = {}
    
    data = unquote(request.args.get("data"))
    
    # Decrypt data from front end
    error, decrypted_data = decrypt(data)
    
    ID = "".join(random.choice(string.ascii_letters + string.punctuation) for _ in range(12))
    
    ID = hashlib.sha256(ID.encode("utf-8")).hexdigest()
    
    response["id"] = ID
    sleep(3)
    
    verification = None
    
    if not error:
        info = json.loads(decrypted_data)
        
        verification = json.dumps({
            "status": 1,
            "id": ID,
            "message": "Verificação iniciada com sucesso!",
            "header": info["header"],
            "token": info["token"],
            "log": "000"
        }).encode("utf-8")
        
        response["result"] = "Success, recebemos a sua requisição!" 
    else:
        verification = json.dumps({
            "status": 0,
            "id": ID,
            "message": "A decriptação do conteúdo falhou!",
            "header": "",
            "token": "",
            "log": "100"
        }).encode("utf-8")
        
        response["result"] = "Error, verifique as informações e refaça a requisição."
    
    if verification:
        record_message_on_kafka_service(PROCESS, verification)
    
    return jsonify(response)

if __name__ == '__main__':
    start()
    
    service.run(
        host="0.0.0.0",
        debug=DEBUG
    )