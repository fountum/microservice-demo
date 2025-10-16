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

    today = datetime.strftime(datetime.now(), app_config['date_format']
)
    # load old stats
    if not os.path.isfile(app_config["datastore"]["filename"]):
        stats = {}
        stats['num_spending_reports'] = 0
        stats['avg_spending'] = 0
        stats['max_spending'] = 0
        stats['total_spending'] = 0
        
        stats['last_updated'] = "2016-01-01 00:00:00"
    else:
        with open(app_config["datastore"]["filename"], "r") as file:
            stats = json.load(file)    
    
    # get data from storage service
    range = {
        "start_timestamp":datetime.strptime(stats["last_updated"], app_config['date_format']),
        "end_timestamp": today
    }
    
        
    res = httpx.get(app_config['eventstores']['spending']['url'], params=range)

    if res.status_code != 200:
        logger.error(f"Failed to get data, {res.status_code=}")
        return 
        
    data = res.json()


    if len(data) != 0:
        # process ridership data
        new_spending = sum([d['spending'] for d in data])


        stats['total_spending'] += new_spending
        stats['avg_spending'] = stats['total_spending'] / (stats["num_spending_reports"] + len(data))
        
        # new total
        stats['num_spending_reports'] += len(data)

        # max 
        for d in data:
            if d['spending'] > stats['max_spending']:
                stats['max_spending'] = d['spending']

        
        # log stats
        logger.debug(f'Spending stats updated: total={stats['total_spending']} avg={stats['avg_spending']} max={stats['max_spending']} total_readings={stats["num_spending_reports"]}')
    else:
        logger.debug(f"No new ridership data")

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

    logger.debug(f'Stats: total={stats['total_spending']} avg={stats['avg_spending']} max={stats['max_spending']} total_readings={stats["num_spending_reports"]}')
    logger.info(f'Request fullfilled')

    return stats,200


if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)