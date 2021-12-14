from flask_apscheduler import APScheduler

from kafka import KafkaClient, KafkaProducer, KafkaConsumer, TopicPartition
from kafka.errors import KafkaError

from time import sleep
import json

PROCESS             = "check_headers"
CHECK_TOKEN_PROCESS = "check_tokens"

def start():
    global offset
    offset = 0
    
    client = KafkaClient(
        bootstrap_servers=["kafka:29092"],
        api_version=(0, 10, 1)
    )
    
    client.add_topic(PROCESS)
    client.close()
    
def is_empty(value):
    if value == None or value == "":
        return True
    else:
        return False

def check_header(header):
    response = True
    
    if header:
        for key, value in header.items():
            if is_empty(value):
                response = False
                break
    else:
        response = False
        
    return response

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
    
    partition = TopicPartition(CHECK_TOKEN_PROCESS, 0)
    requestion_consumer.assign([partition])
    requestion_consumer.seek(partition, offset)
    
    for request in requestion_consumer:
        offset = request.offset +1
        
        json_request = request.value
        request_information = json.loads(json_request)
        header = request_information["header"]
        
        id = request_information["id"]
        status = request_information["status"]
        message = request_information["message"]
        log = request_information["log"]
        
        response = check_header(header)
        
        if status != 0:
            if response:
                verification = json.dumps({
                    "status": 1,
                    "id": id,
                    "message": "Sucesso na verificação do cabeçalho!",
                    "header": request_information["header"],
                    "token": request_information["token"],
                    "user": request_information["user"],
                    "log": "000"
                }).encode("utf-8")
                
                record_message_on_kafka_service(PROCESS, verification)
            else:
                verification = json.dumps({
                    "status": 0,
                    "id": id,
                    "message": response,
                    "header": "",
                    "token": "",
                    "user": "",
                    "log": "001"
                }).encode("utf-8")
                
                record_message_on_kafka_service(PROCESS, verification)
        else:
            verification = json.dumps({
                "status": 0,
                "id": id,
                "message": message,
                "header": "",
                "token": "",
                "log": log
            }).encode("utf-8")
            
            record_message_on_kafka_service(PROCESS, verification)

if __name__ == "__main__":
    start()
    
    scheduler = APScheduler()
    scheduler.add_job(id=PROCESS, func=execute, trigger="interval", seconds=3)
    
    scheduler.start()
    
    while True:
        sleep(60)