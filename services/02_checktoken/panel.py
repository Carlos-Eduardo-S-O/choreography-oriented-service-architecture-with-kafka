import json
from kafka import TopicPartition
from time import sleep

from kafka.consumer.group import KafkaConsumer

request_panel = KafkaConsumer(
    bootstrap_servers=["kafka:29092"],
    api_version=(0, 10, 1),
    
    auto_offset_reset="earliest",
    consumer_timeout_ms=1000
)

partition = TopicPartition("check_tokens", 0)
request_panel.assign([partition])

request_panel.seek_to_beginning(partition)
offset = 0

while True:
    print("Esperando por tokens para analisar...")
    
    for request in request_panel:
        offset = request.offset + 1
        
        request_data = json.loads(request.value)
        print(f"Resultado da verificação: {request_data}")
        
    request_panel.seek(partition, offset)
        
    sleep(5)
    