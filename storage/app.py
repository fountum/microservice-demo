from datetime import datetime
import connexion
from connexion import NoContent
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
import yaml
import logging.config
from models import Spending

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

DATE_FORMAT = app_config['date_format']

def report_spending(body):
    session = make_session()

    event = Spending(
        trace_id=body['trace_id'],
        spending = body['spending'],
        reported_time = body['reported_time']  
    )

    session.add(event)
    session.commit()
    session.close()

    logger.debug(f'Stored event spending trace_id={body['trace_id']}')
    return NoContent,201

def get_spending(start_timestamp, end_timestamp):
    session = make_session()
    start = datetime.strptime(start_timestamp, DATE_FORMAT)
    end = datetime.strptime(end_timestamp, DATE_FORMAT)

    statement = select(Spending).where(Spending.date_created >= start).where(Spending.date_created < end)
    print(str(statement))
    results = [result.to_dict() for result in session.execute(statement).scalars().all()] 

    session.close()

    logger.debug("Found %d Spending readings (start: %s, end: %s)", len(results), start, end)

    return results

if __name__ == "__main__":
    app.run(port=8090)