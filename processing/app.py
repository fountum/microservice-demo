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
from pymongo import MongoClient,DESCENDING

app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

# loading config
with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

# mongodb connection
client = MongoClient(app_config['datastore']['database'])
db = client['sales_stats'] # ?
collection = db["stats"]

# logging
logger = logging.getLogger('basicLogger')

def populate_stats():
    logger.info(f'Starting routine stats generating')

    today = datetime.strftime(datetime.now(), app_config['date_format'])
    # load old stats

    entry = collection.find_one(sort=[( '_id', DESCENDING)])

    if entry == None:
        stats = {}
        stats['num_sales_reports'] = 0
        stats['avg_income'] = 0
        stats['avg_customers'] = 0
        stats['avg_cookies_sold'] = 0
        stats['max_income'] = 0
        stats['max_customers'] = 0
        stats['max_cookies_sold'] = 0
        stats['min_income'] = 999999
        stats['min_customers'] = 999999
        stats['min_cookies_sold'] = 999999
        stats['total_income'] = 0
        stats['total_customers'] = 0
        stats['total_cookies_sold'] = 0
        
        stats['last_updated'] = "2016-01-01 00:00:00"
    else:
        stats = entry
         
    
    # get data from storage service
    range = {
        "start_timestamp":datetime.strptime(stats["last_updated"], app_config['date_format']),
        "end_timestamp": today
    }
    
        
    res = httpx.get(app_config['eventstores']['sales']['url'], params=range)

    if res.status_code != 200:
        logger.error(f"Failed to get data, {res.status_code=}")
        return 
        
    data = res.json()


    if len(data) != 0:
        # process data
        new_income = sum([d['income'] for d in data])
        new_customers = sum([d['customers'] for d in data])
        new_cookies_sold = sum([d['cookies_sold'] for d in data])

        stats['num_sales_reports'] += len(data)

        stats['total_income'] += new_income
        stats['total_customers'] += new_customers
        stats['total_cookies_sold'] += new_cookies_sold

        stats['avg_income'] = stats['total_income'] / stats['num_sales_reports']
        stats['avg_customers'] = stats['total_customers'] / stats['num_sales_reports']
        stats['avg_cookies_sold'] = stats['total_cookies_sold'] / stats['num_sales_reports']

        # max 
        for d in data:
            if d['income'] > stats['max_income']:
                stats['max_income'] = d['income']
            if d['customers'] > stats['max_customers']:
                stats['max_customers'] = d['customers']
            if d['cookies_sold'] > stats['max_cookies_sold']:
                stats['max_cookies_sold'] = d['cookies_sold']

            if d['income'] < stats['min_income']:
                stats['min_income'] = d['income']
            if d['customers'] < stats['min_customers']:
                stats['min_customers'] = d['customers']
            if d['cookies_sold'] < stats['min_cookies_sold']:
                stats['min_cookies_sold'] = d['cookies_sold']
            

        
        # log stats
        logger.debug(f'Sales stats updated: total_sales={stats['num_sales_reports']}')
        logger.debug(f'Income: total={stats['total_income']} avg={stats['avg_income']} min={stats['min_income']} max={stats['max_income']}')
        logger.debug(f'customers: total={stats['total_customers']} avg={stats['avg_customers']} min={stats['min_customers']} max={stats['max_customers']}')
        logger.debug(f'cookies_sold: total={stats['total_cookies_sold']} avg={stats['avg_cookies_sold']} min={stats['min_cookies_sold']} max={stats['max_cookies_sold']}')
    else:
        logger.debug(f"No new ridership data")

    stats['last_updated'] = today

    # write to MongoDB
    collection.delete_one(entry)
    collection.insert_one(stats)
        

    # writing to JSON
    # with open(app_config["datastore"]["filename"], "w") as file:
    #     json.dump(stats, file)

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

    entry = collection.find_one(sort=[( '_id', DESCENDING)])

    if entry == None:
        logger.error(f"{app_config["datastore"]["database"]} did not send data")
        return "Statistics do not exist", 404
    else:
        stats = entry


    logger.debug(f'Sales stats updated: total_sales={stats['num_sales_reports']}')
    logger.debug(f'Income: total={stats['total_income']} avg={stats['avg_income']} min={stats['min_income']} max={stats['max_income']}')
    logger.debug(f'customers: total={stats['total_customers']} avg={stats['avg_customers']} min={stats['min_customers']} max={stats['max_customers']}')
    logger.debug(f'cookies_sold: total={stats['total_cookies_sold']} avg={stats['avg_cookies_sold']} min={stats['min_cookies_sold']} max={stats['max_cookies_sold']}')
    logger.info(f'Request fullfilled')

    stats.pop('_id')

    return stats,200


if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)