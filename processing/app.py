from datetime import datetime
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

date_format = "%Y-%m-%d %H:%M:%S"


# loading config
with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

# logging
logger = logging.getLogger('basicLogger')


def populate_stats():
    logger.info(f'Starting routine stats generating')

    today = datetime.strftime(datetime.now(), date_format)
    # load old stats
    if not os.path.isfile(app_config["datastore"]["filename"]):
        stats = {}
        stats['num_ridership_readings'] = 0
        stats['avg_ridership'] = 0
        stats['num_fuel_readings'] = 0
        stats['min_fuel_litres'] = 0
        stats['max_fuel_litres'] = 0
        
        stats['last_updated'] = "2016-01-01 00:00:00"
    else:
        with open(app_config["datastore"]["filename"], "r") as file:
            stats = json.load(file)    
    
    # get data from storage service
    range = {
        "start_timestamp":datetime.strptime(stats["last_updated"], date_format),
        "end_timestamp": today
    }
    
        
    r_ridership = httpx.get(app_config['eventstores']['ridership']['url'], params=range)
    r_fuel= httpx.get(app_config['eventstores']['fuel']['url'], params=range)

    if r_ridership.status_code != 200 or r_fuel.status_code != 200:
        logger.error(f"Failed to get data, {r_ridership.status_code=} {r_fuel.status_code=}")
        return 
        
    data_ridership = r_ridership.json()
    data_fuel = r_fuel.json()

    if len(data_ridership) != 0:
        data_ridership = data_ridership
        # process ridership data
        new_passengers = sum([d['passengers_boarded'] for d in data_ridership])
        old_passengers = stats['avg_ridership'] * stats["num_ridership_readings"]
        stats['avg_ridership'] = (old_passengers + new_passengers) / (stats["num_ridership_readings"] + len(data_ridership))
        
        stats['num_ridership_readings'] += len(data_ridership)

        # log stats
        logger.debug(f'Ridership stats updated: avg={stats['avg_ridership']} total_readings={stats["num_ridership_readings"]}')
    else:
        logger.debug(f"No new ridership data")

    # process fuel data
    if len(data_fuel) != 0:
        data_fuel = data_fuel
        for d in data_fuel:
            if d['fuel_litres'] > stats['max_fuel_litres']:
                stats['max_fuel_litres'] = d['fuel_litres']
            
            if d['fuel_litres'] > stats['min_fuel_litres']:
                stats['min_fuel_litres'] = d['fuel_litres']
        
        stats['num_fuel_readings'] += len(data_fuel)
        logger.debug(f'Fuel stats updated:  min={stats['min_fuel_litres']} max={stats['max_fuel_litres']} total_readings={stats['num_fuel_readings']}')
    else:
        logger.debug(f"No new fuel data")

    stats['last_updated'] = today

    # writing to JSON
    with open(app_config["datastore"]["filename"], "w") as file:
        json.dump(stats, file)

    logger.info(f'Stats generation completed')


# scheduler
def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
        'interval',
        seconds=app_config['scheduler']['interval'])
    sched.start()
    logger.debug('SCHEDULER GO')
    
# /stats
def get_stats():
    logger.info("GET request recieved")

    if not os.path.isfile(app_config["datastore"]["filename"]):
        logger.error(f"{app_config["datastore"]["filename"]} does not exist")
        return "Statistics do not exist", 404
    else:
        with open(app_config["datastore"]["filename"], "r") as file:
            stats = json.load(file)    

    logger.debug(f'Stats: {stats['avg_ridership']=} {stats['max_fuel_litres']} {stats['min_fuel_litres']}')
    logger.info(f'Request fullfilled')

    return stats,200


if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)