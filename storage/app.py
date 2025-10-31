from datetime import datetime
import json
from threading import Thread
import connexion
from connexion import NoContent
from pykafka import KafkaClient
import pykafka
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
import yaml
import logging.config
from models import Fuel, Ridership

# loading config
with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

# db connection
ENGINE = create_engine(app_config['database'])
def make_session():
    return sessionmaker(bind=ENGINE)()

app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

# logger
logger=logging.getLogger('basicLogger')

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def process_messages():
    """ Process event messages """
    hostname = f"{app_config["events"]["hostname"]}:{app_config["events"]["port"]}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]
    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
        reset_offset_on_start=False,
        auto_offset_reset=pykafka.common.OffsetType.LATEST)
    # This is blocking - it will wait for a new message

    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]
        if msg["type"] == "ridership":
            report_ridership_reading(payload)
            
        elif msg["type"] == "fuel": 
            report_fuel_reading(payload)
            
        consumer.commit_offsets()

# enables listening for Kafka messages
def setup_kafka_thread():
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()

def report_ridership_reading(body):
    session = make_session()

    event = Ridership(
        trace_id=body['trace_id'],
        bus_id=body['bus_id'],
        route_name=body['route_name'],
        stop_id=body['stop_id'],
        passengers_boarded=body['passengers_boarded'],
        recorded_timestamp=datetime.strptime(body['recorded_timestamp'], DATE_FORMAT),
        batch_timestamp=datetime.strptime(body['batch_timestamp'], DATE_FORMAT)
    )

    session.add(event)
    session.commit()
    session.close()

    logger.debug(f'Stored event ridership trace_id={body['trace_id']}')
    return NoContent,201

def get_ridership_reading(start_timestamp, end_timestamp):
    session = make_session()
    start = datetime.strptime(start_timestamp, DATE_FORMAT)
    end = datetime.strptime(end_timestamp, DATE_FORMAT)

    statement = select(Ridership).where(Ridership.date_created >= start).where(Ridership.date_created < end)
    print(str(statement))
    results = [result.to_dict() for result in session.execute(statement).scalars().all()] 

    session.close()

    logger.debug("Found %d bus ridership readings (start: %s, end: %s)", len(results), start, end)

    return results

def report_fuel_reading(body):
    session = make_session()

    event = Fuel(
        trace_id=body['trace_id'],
        bus_id=body['bus_id'],
        route_name=body['route_name'],
        fuel_litres=body['fuel_litres'],
        recorded_timestamp=datetime.strptime(body['recorded_timestamp'], DATE_FORMAT),
        batch_timestamp=datetime.strptime(body['batch_timestamp'], DATE_FORMAT)
    )

    session.add(event)
    session.commit()
    session.close()

    logger.debug(f'Stored event fuel trace_id={body['trace_id']}')
    return NoContent,201  

def get_fuel_reading(start_timestamp, end_timestamp):
    session = make_session()
    start = datetime.strptime(start_timestamp, DATE_FORMAT)
    end = datetime.strptime(end_timestamp, DATE_FORMAT)

    statement = select(Fuel).where(Fuel.date_created >= start).where(Fuel.date_created < end)
    results = [result.to_dict() for result in session.execute(statement).scalars().all()] 

    session.close()

    logger.debug("Found %d bus Fuel readings (start: %s, end: %s)", len(results), start, end)

    return results

if __name__ == "__main__":
    setup_kafka_thread()
    app.run(port=8090)