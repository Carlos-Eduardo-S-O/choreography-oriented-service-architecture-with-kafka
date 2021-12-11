from flask_apscheduler import APScheduler

from kafka import KafkaClient, KafkaProducer, TopicPartition
from kafka.errors import KafkaError

from time import sleep
import json
import jwt
from kafka.structs import OffsetAndMetadata

PROCESS             = "verify_headers"
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
    
def is_empty():
    pass
    
def verify_header(header):
    response = True
    
    if header:
        for key, value in header.items():
            if is_empty():
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
    pass

if __name__ == "__main__":
    start()
    
    scheduler = APScheduler()
    scheduler.add_job(id=PROCESS, func=execute, trigger="interval", seconds=3)
    
    scheduler.start()
    
    while True:
        sleep(60)