'''
    This is an alterative version of the processing service that offers more realistic ableit more complicated statistics
    not used because it's too much to maintain.
'''


import datetime
import json
import logging.config
import uuid
import connexion
from connexion import NoContent
import os
import httpx
import yaml
from apscheduler.schedulers.background import BackgroundScheduler

app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

# loading config
with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

# logging
logger = logging.getLogger('basicLogger')


def populate_stats():
    print("POPULATE STATS")
    trace_id = str(uuid.uuid4())

    logger.info(f'Starting routine stats generating {trace_id=}')

    # load old stats
    if not os.path.isfile("bus_stats.json"):
        stats = []
        stats['num_ridership_readings'] = 0
        stats['avg_ridership'] = 0
        stats['num_fuel_readings'] = 0
        stats['routes'] = []
        stats['min_fuel_litres'] = 0
        stats['max_fuel_litres'] = 0
        
        
        stats['last_updated'] = datetime.datetime.fromisoformat("2016-01-01t00:00:00z")
    else:
        with open("bus_stats.json", "r") as file:
            stats = json.load(file)    
    
    # get data from storage service
    today = datetime.datetime.today()
    range = {
        "start_date":stats["last_updated"],
        "end_date": datetime.datetime.today()
    }
    stats['last_update'] = today
    
    r_ridership = httpx.get(app_config['data']['ridership'], params=range)
    r_fuel= httpx.get(app_config['data']['fuel'], params=range)

    if r_ridership.status_code != 200 or r_fuel != 200:
        logger.error(f"Failed to get data, {r_ridership.status_code=} {r_fuel.status_code=}")
        return NoContent, 400 #?
    
    data_ridership = r_ridership.text
    data_fuel = r_fuel.text

    # process data
    new_passengers = sum([d['passengers_boarded'] for d in data_ridership])
    old_passengers = stats['avg_ridership'] * stats["num_ridership_readings"]
    stats['avg_ridership'] = (old_passengers + new_passengers) / (stats["num_ridership_readings"] + len(data_ridership))
    
    stats['num_ridership_readings'] += len(data_ridership)

    # log stats
    logger.debug(f'Ridership stats updated: avg={stats['avg_ridership']} total_readings={stats["num_ridership_readings"]}')

    # find routes
    '''
        this is a  simplified implementation of what was proposed; maybe i can fix it but it'll do for now...
    '''
    # list of routes processed to avoid a massive debug message
    routes_processed = set()

    for d in data_fuel:
        routes_processed.add(d['route_name'])
        if d['route_name']in stats['routes']:
            # without this it's so unreadable LOL
            route_stats = stats['routes'][d['route_name']]
            
            if d["fuel_litres"] > route_stats['max_fuel_litres']:
                route_stats['max_fuel_litres'] = d["fuel_litres"]

            elif d["fuel_litres"] < route_stats['min_fuel_litres']:
                route_stats['min_fuel_litres'] = d["fuel_litres"]
            
            route_stats['avg_fuel_litres'] = (route_stats['avg_fuel_litres'] * route_stats['sample_size'] + d['fuel_litres']) / (route_stats['sample_size'] + 1)

        else:
            route_stats = {
                "route_name": d['route_name'],
                "max_fuel_litres": d['fuel_litres'],
                "min_fuel_litres": d['fuel_litres'],
                "avg_fuel_litres": d['fuel_litres'],
                "sample_size": 1
            }

        route_stats['last_updated'] = d['recorded_timestamp']
        stats['routes'][d['route_name']] = route_stats

    # log debugger stats
    for route_name in routes_processed:
        route_stats = stats['routes'][route_name]
        logger.debug(f'{route_name=} fuel stats updated: min={route_stats['min_fuel_litres']} max={route_stats['max_fuel_litres']} avg={route_stats['avg_fuel_litres']} sample_size={route_stats['sample_size']}')
    
    stats['num_fuel_readings'] += len(data_fuel)
    logger.debug(f'completed processing fuel: total_readings={stats['num_fuel_readings']}')



    # writing to JSON
    with open("bus_stats.json", "w") as file:
        json.dump(stats)

    logger.info(f'Stats generation completed {trace_id=}')

    # might be wrong? maybe use the last recorded timestamp
    stats['last_updated'] = today

# scheduler
def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
        'interval',
        seconds=app_config['scheduler']['interval'])
    sched.start()
    
# /stats
def get_stats(body):
    logger.info("GET request recieved")

    if not os.path.isfile("bus_stats.json"):
        logger.error("Log file does not exist")
        return "Statistics do not exist", 404
    else:
        with open("bus_stats.json", "r") as file:
            stats = json.load(file)    

    logger.debug(f'Stats: {stats['avg_ridership']=} {len(stats['routes'])}')
    logger.info(f'Request fullfilled')
    return stats,200


if __name__ == "__main__":
    app.run(port=8100)