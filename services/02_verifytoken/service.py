from flask_apscheduler import APScheduler

from kafka import KafkaClient, KafkaProducer, KafkaConsumer, TopicPartition
from kafka.errors import KafkaError

from time import sleep
import json
import jwt

PROCESS             = "verify_tokens"
CRIPTOGRAFY_PROCESS = "criptografy"

TOKEN_KEY           = "secret key"

def start():
    global offset
    offset = 0
    
    client =  KafkaClient(
        bootstrap_servers=["kafka:29092"],
        api_version=(90, 10, 1)
    )
    
    client.add_topic(PROCESS)
    client.close()
    
def get_token_key():
    return TOKEN_KEY

def verify_token(token):
    response = "ok"
    user = None
    key = get_token_key()
    
    if token:
        try: 
            response = jwt.decode(token, key, algorithms="HS256")
        except: 
            response = "Token inválido."
    else:
        response = "O token não existe."
    
    return response, user
    
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
    
def execute():
    global offset
    result = "ok"
    
    requestion_consumer = KafkaConsumer(
        bootstrap_servers=["kafka:29092"],
        api_version = (0, 10, 1),
        auto_offset_reset="earliest",
        consumer_timeout_ms=1000
    )
    
    partition = TopicPartition(CRIPTOGRAFY_PROCESS, 0)
    requestion_consumer.assign([partition])
    requestion_consumer.seek(partition, offset)
    
    for request in requestion_consumer:
        offset = request.offset +1
        
        json_request = request.value
        request_information = json.loads(json_request)
        token = request_information["token"]
        
        id = request_information["id"]
        status = request_information["status"]
        
        response, user = verify_token(token)
        
        if status != 0:
            if user:
                verification = json.dumps({
                    "status": 1,
                    "id": id,
                    "message": "Sucesso na verificação do token!",
                    "header": request_information["header"],
                    "token": request_information["token"],
                    "user": user
                }).encode("utf-8")
                
                record_message_on_kafka_service(PROCESS, verification)
            else:
                verification = json.dumps({
                    "status": 0,
                    "id": id,
                    "message": response,
                    "header": "",
                    "token": ""
                }).encode("utf-8")
                
                record_message_on_kafka_service(PROCESS, verification)

if __name__ == "__main__":
    start()
    
    scheduler = APScheduler()
    scheduler.add_job(id=PROCESS, func=execute, trigger="interval", seconds=3)
    
    scheduler.start()
    
    while True:
        sleep(60)