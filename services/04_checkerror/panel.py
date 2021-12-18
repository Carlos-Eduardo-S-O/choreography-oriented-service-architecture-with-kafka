import json
from kafka import TopicPartition
from time import sleep
from datetime import datetime
from colored import fg as foreground, attr as attibute
from kafka.consumer.group import KafkaConsumer

RED   = foreground("red")
GREEN = foreground("green")
RESET = attibute("reset")

def header(id):
    aux_print()
    print(f"------ID: {id}------")
    aux_print()

def body(status, verification, header, token, payload, datetime):
    if status == 0:
        verification = f"{RED}{verification}{RESET}"
    else:
        verification = f"{GREEN}{verification}{RESET}"
        
    print(f"Resposta das verificações: {verification}")
    
    if header != "":
        print("Cabeçalho da requisição:")
        print_header(header)
    else:
        print("Cabeçalho da requisição: sem informações")
    
    if payload != "":
        print("Informações do usuário:")
        print_user(payload)
    else:
        print("Informações do usuário: sem informações")
    
    if token != "":
        print(f"Token de autenticação:\n{token}")
    else: 
        print("Token de autenticação: sem informações")
    
    print(f"requisição verificada às: {datetime}")

def print_header(header):
    space    = "   -"
    ip       = header["ip"]
    author   = header["author"]
    api      = header["api"]
    device   = header["device"]
    location = header["location"] 
    
    text_to_print = [
        f"{space}ip: {ip}    |   localização: {location}", 
        f"{space}autor: {author}    |   api: {api}",
        f"{space}dispositivo: {device}"
    ]
    
    for text in text_to_print:
        print(text)

def print_user(payload):
    space = "   -"
    user  = payload["user"]
    
    id   = user["id"]
    name = user["name"]
    age  = user["age"]
    
    timestamp = payload["exp"]
    
    expiration_date = datetime.fromtimestamp(timestamp)
    
    text_to_print = [
        f"{space}id: {id}",
        f"{space}name: {name}   |   age: {age}",
        f"{space}data de expiração de autenticação: {expiration_date}"
    ]

    for text in text_to_print:
        print(text)
    
def footer():
    aux_print()

def aux_print():
    print("-"*80)

def print_info(info):
    status  = info["status"]
    id      = info["id"]
    verification = info["verification"]
    request_header  = info["header"]
    token   = info["token"]
    payload = info["user"]
    datetime = info["datetime"]
    
    print()
    header(id)
    body(status, verification,request_header, token, payload, datetime)
    footer()
    print()
    
def goodbye():
    print("\nDesligando o painel...")
    sleep(2)
    print("Obrigado por utilizar os nossos serviços")
    
request_panel = KafkaConsumer(
    bootstrap_servers=["kafka:29092"],
    api_version=(0, 10, 1),
    
    auto_offset_reset="earliest",
    consumer_timeout_ms=1000
)

partition = TopicPartition("check_error", 0)
request_panel.assign([partition])

request_panel.seek_to_beginning(partition)

offset = 0

try:
    while True:
        print("Esperando requisições...")
        
        for request in request_panel:
            offset = request.offset + 1
            
            request_data = json.loads(request.value)
            
            print_info(request_data)
            
        request_panel.seek(partition, offset)
            
        sleep(5)
except KeyboardInterrupt:
    goodbye()