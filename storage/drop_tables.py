from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import yaml

# loading config
with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

ENGINE = create_engine(app_config['database'])
def make_session():
    return sessionmaker(bind=ENGINE)()

Base.metadata.drop_all(ENGINE)