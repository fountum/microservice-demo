from datetime import datetime
import connexion
from connexion import NoContent
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

date_format = "%Y-%m-%d %H:%M:%S"

def report_ridership_reading(body):
    session = make_session()

    event = Ridership(
        trace_id=body['trace_id'],
        bus_id=body['bus_id'],
        route_name=body['route_name'],
        stop_id=body['stop_id'],
        passengers_boarded=body['passengers_boarded'],
        recorded_timestamp=datetime.strptime(body['recorded_timestamp'], date_format),
        batch_timestamp=datetime.strptime(body['batch_timestamp'], date_format)
    )

    session.add(event)
    session.commit()
    session.close()

    logger.debug(f'Stored event ridership trace_id={body['trace_id']}')
    return NoContent,201

def get_ridership_reading(start_timestamp, end_timestamp):
    session = make_session()
    start = datetime.strptime(start_timestamp, date_format)
    end = datetime.strptime(end_timestamp, date_format)

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
        recorded_timestamp=datetime.strptime(body['recorded_timestamp'], date_format),
        batch_timestamp=datetime.strptime(body['batch_timestamp'], date_format)
    )

    session.add(event)
    session.commit()
    session.close()

    logger.debug(f'Stored event fuel trace_id={body['trace_id']}')
    return NoContent,201  

def get_fuel_reading(start_timestamp, end_timestamp):
    session = make_session()
    start = datetime.strptime(start_timestamp, date_format)
    end = datetime.strptime(end_timestamp, date_format)

    statement = select(Fuel).where(Fuel.date_created >= start).where(Fuel.date_created < end)
    results = [result.to_dict() for result in session.execute(statement).scalars().all()] 

    session.close()

    logger.debug("Found %d bus Fuel readings (start: %s, end: %s)", len(results), start, end)

    return results

if __name__ == "__main__":
    app.run(port=8090)