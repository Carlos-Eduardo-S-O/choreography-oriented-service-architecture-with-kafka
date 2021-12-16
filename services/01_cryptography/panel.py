import json
from kafka import TopicPartition
from time import sleep
from colored import fg as foreground, attr as attibute
from kafka.consumer.group import KafkaConsumer

RED   = foreground("red")
GREEN = foreground("green")
RESET = attibute("reset")

def header(id):
    aux_print()
    print(f"------ID: {id}------")
    aux_print()

def body(status, message, header, token):
    message = f"{GREEN}{message}{RESET}"
    
    if status == 0:
        message = f"{RED}{message}{RESET}"
        
    print(f"Resposta do sistema: {message}")
    print("Cabeçalho da requisição:")
    print_header(header)
    print(f"Token de autenticação:\n{token}")

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

def footer():
    aux_print()

def aux_print():
    print("-"*80)

def print_info(info):
    status  = info["status"]
    id      = info["id"]
    message = info["message"]
    request_header  = info["header"]
    token   = info["token"]
    
    print()
    header(id)
    body(status, message, request_header, token)
    footer()
    print()
    
def goodbye():
    print("Desligando o painel...")
    sleep(2)
    print("Obrigado por utilizar os nossos serviços")

request_panel = KafkaConsumer(
    bootstrap_servers=["kafka:29092"],
    api_version=(0, 10, 1),
    
    auto_offset_reset="earliest",
    consumer_timeout_ms=1000
)

partition = TopicPartition("criptografy", 0)
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
    

    