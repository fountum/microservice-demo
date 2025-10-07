from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

ENGINE = create_engine("mysql://bus_api:superbass@localhost/bus_data")
def make_session():
    return sessionmaker(bind=ENGINE)()

Base.metadata.drop_all(ENGINE)