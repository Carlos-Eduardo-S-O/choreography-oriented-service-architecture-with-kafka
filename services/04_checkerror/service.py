from flask_apscheduler import APScheduler

from kafka import KafkaClient, KafkaProducer, KafkaConsumer, TopicPartition
from kafka.errors import KafkaError

from time import sleep
from datetime import datetime
import json

PROCESS              = "check_error"
CHECK_HEADER_PROCESS = "check_headers"

MESSAGES = {
    "cripto" : "Por favor, verifique suas chaves de acesso.",
    "token"  : "Existe um problema com o seu token de autenticação, tente logar novamente.",
    "header" : "Por favor, preencha todas as informações do cabeçalho corretamente e tente novamente.",
    "success": "Requisição verificada com sucesso."
}

def start():
    global offset
    offset = 0
    
    client = KafkaClient(
        bootstrap_servers=["kafka:29092"],
        api_version=(0, 10, 1)
    )
    
    client.add_topic(PROCESS)
    client.close()
    
def SUCCESS():
    return MESSAGES["success"]

def CRIPTO_ERROR():
    return MESSAGES["cripto"]

def TOKEN_ERROR():
    return MESSAGES["token"]

def HEADER_ERROR():
    return MESSAGES["header"]

def check_error(log):
    verification_flag = {
        "000": SUCCESS(),
        "100": CRIPTO_ERROR(),
        "010": TOKEN_ERROR(),
        "001": HEADER_ERROR()
    }
    
    result = verification_flag[log]
    
    return result
    


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
    
    partition = TopicPartition(CHECK_HEADER_PROCESS, 0)
    requestion_consumer.assign([partition])
    requestion_consumer.seek(partition, offset)

    for request in requestion_consumer:
        offset = request.offset +1
        
        json_request = request.value
        request_information = json.loads(json_request)
        
        log = request_information["log"]
        status = request_information["status"]
        
        response = str(check_error(log))
        request_verification_date = str(datetime.utcnow())
        
        if status == 1:
            verification = json.dumps({
                "id": request_information["id"],
                "header": request_information["header"],
                "token": request_information["token"],
                "user": request_information["user"],
                "verification": response,
                "datetime": request_verification_date
            }).encode("utf-8")

            record_message_on_kafka_service(PROCESS, verification)
        else:
            verification = json.dumps({
                "id": request_information["id"],
                "header": request_information["header"],
                "token": request_information["token"],
                "verification": response,
                "datetime": request_verification_date
            }).encode("utf-8")
            
            record_message_on_kafka_service(PROCESS, verification)
if __name__ == "__main__":
    start()
    
    scheduler = APScheduler()
    scheduler.add_job(id=PROCESS, func=execute, trigger="interval", seconds=3)
    
    scheduler.start()
    
    while True:
        sleep(60)
        