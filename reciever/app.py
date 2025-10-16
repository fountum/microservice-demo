import logging.config
import uuid
import connexion
from connexion import NoContent
import os
import httpx
import yaml
from datetime import datetime

app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

DATE_FORMAT = "%Y/%m/%d %H:%M:%S"

# load configs
with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    logging.config.dictConfig(LOG_CONFIG)

# logging
logger = logging.getLogger('basicLogger')

# /spending/report
def report_spending(body):
    trace_id = str(uuid.uuid4())
    logger.debug(f'Recieved event ridership {trace_id=}')

    body['reported_time'] = datetime.now().strftime(DATE_FORMAT)
    body['trace_id'] = trace_id
    logger.debug(f'{body=}')
    
    r= httpx.post(app_config['events']['spending'],json=body)
        
    logger.debug(f'Response for event spending {trace_id=}, {r.status_code=}')
    return NoContent,r.status_code


if __name__ == "__main__":
    app.run(port=8080)