from pykafka import KafkaClient
import json
from datetime import datetime
import uuid
import time
import glob

# KAFKA PRODUCER
client = KafkaClient(hosts="localhost:9092")
topic = client.topics['bus_data_topic']
producer = topic.get_sync_producer()

coordinates_array = []
input_files = glob.glob("data/*.json")
for file_name in input_files:
    with open(file_name) as file:
        coordinates_array.append(json.load(
            file)['features'][0]['geometry']['coordinates'])

bus_data = [{'busline': '00001'}, {'busline': '00002'}, {'busline': '00003'}]

# GENERATE UUID


def get_uuid():
    return uuid.uuid4()


def generate_checkpoint(bus_data, coordinates_array):
    i = 0
    length = len(coordinates_array[0])
    while i < length:
        for index, data in enumerate(bus_data):
            coordinates = coordinates_array[index]
            data['key'] = data['busline'] + '_' + str(get_uuid())
            data['timestamp'] = str(datetime.utcnow())
            data['latitude'] = coordinates[i][1]
            data['longitude'] = coordinates[i][0]
            message = json.dumps(data)
            print(message)
            producer.produce(message.encode('ascii'))
            time.sleep(0.5)

        # if bus reaches last coordinate, start from beginning
        if i == (length-1):
            i = 0
        else:
            i += 1


generate_checkpoint(bus_data, coordinates_array)
