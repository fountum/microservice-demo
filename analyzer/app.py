from datetime import datetime
import json
from threading import Thread
import connexion
from connexion import NoContent
from pykafka import KafkaClient
import pykafka
import yaml
import logging.config
from models import Fuel, Ridership

# loading config
with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

# logger
logger=logging.getLogger('basicLogger')

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# /bus/ridership
def get_ridership_reading(index):
    hostname = f"{app_config["events"]["hostname"]}:{app_config["events"]["port"]}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]
    consumer = topic.get_simple_consumer(
        reset_offset_on_start=False,
        consumer_timeout_ms=1000) # kills consumer when it doesn't receive msg after x ms
    
    counter = 0
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        
        # find reading 
        logger.debug(msg)
        if msg['type'] == 'ridership':
            if counter == index:
                return msg['payload'], 200
            counter+=1
    logger.info(f'Found {counter} ridership readings')
    return NoContent, 404


# /bus/fuel
def get_fuel_reading(index):
    hostname = f"{app_config["events"]["hostname"]}:{app_config["events"]["port"]}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]
    consumer = topic.get_simple_consumer(
        reset_offset_on_start=False,
        consumer_timeout_ms=1000) # kills consumer when it doesn't receive msg after x ms
    
    counter = 0
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        
        # find reading 
        logger.debug(msg)
        if msg['type'] == 'fuel':
            if counter == index:
                return msg['payload'], 200
            counter+=1
    logger.info(f'Found {counter} fuel readings')
    return NoContent, 404

def get_stats():
    hostname = f"{app_config["events"]["hostname"]}:{app_config["events"]["port"]}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]
    consumer = topic.get_simple_consumer(
        reset_offset_on_start=False,
        consumer_timeout_ms=1000) # kills consumer when it doesn't receive msg after x ms
    
    stats = {
        'num_ridership_readings' : 0,
        'num_fuel_readings' : 0
    }
    
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        # logger.info("Message: %s" % msg)
        
        # find reading 
        logger.debug(msg)
        if msg['type'] == 'ridership':
            stats['num_ridership_readings']+=1
        elif msg['type'] == 'fuel':
            stats['num_fuel_readings']+=1
    logger.info(f'Ridership:{stats['num_ridership_readings']}  Fuel:{stats['num_fuel_readings']}')
    return stats, 200



if __name__ == "__main__":
    app.run(port=8110)