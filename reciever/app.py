import json
import logging.config
import uuid
import connexion
from connexion import NoContent
import os
import httpx
import yaml

app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

MAX_BATCH_EVENTS = 5
RIDERSHIP_FILE = 'ridership.json'
FUEL_FILE = 'fuel.json'

# load configs
with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    logging.config.dictConfig(LOG_CONFIG)

# logging
logger = logging.getLogger('basicLogger')

# /bus/ridership
def report_ridership_reading(body):
    trace_id = str(uuid.uuid4())
    logger.debug(f'Recieved event ridership {trace_id=}')

    skeleton = body.copy()
    skeleton['trace_id']=trace_id
    readings = skeleton.pop("readings")
    
    for d in readings:
        data = skeleton.copy()
        data['recorded_timestamp']=d['recorded_timestamp']
        data['stop_id']=d['stop_id']
        data['passengers_boarded']=d['passengers_boarded']
        print(data)
        r= httpx.post(app_config['events']['ridership'],json=data)
        
    logger.debug(f'Response for event ridership {trace_id=}, {r.status_code=}')
    return NoContent,r.status_code

# /bus/fuel
def report_fuel_reading(body):
    trace_id = str(uuid.uuid4())
    logger.debug(f'Recieved event fuel {trace_id=}')

    skeleton = body.copy()
    readings = skeleton.pop("readings")
    
    for d in readings:
        data = skeleton.copy()
        data['trace_id']=trace_id
        data['recorded_timestamp']=d['recorded_timestamp']
        data['fuel_litres']=d['fuel_litres']
        
        r= httpx.post(app_config["events"]['fuel'],json=data)
    logger.debug(f'Response for event fuel {trace_id=}, {r.status_code=}')

    return NoContent,r.status_code


if __name__ == "__main__":
    app.run(port=8080)