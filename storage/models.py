from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer, String, DateTime, func, Float
from datetime import datetime
import yaml

# loading config
with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

class Base(DeclarativeBase):
    pass

class Sale(Base):
    __tablename__ = "sales"
    id = mapped_column(Integer, primary_key=True)
    trace_id = mapped_column(String(36), nullable=False)
    customers = mapped_column(Integer, nullable=False)
    cookies_sold = mapped_column(Integer, nullable=False)
    income = mapped_column(Float, nullable=False)
    reported_time = mapped_column(DateTime, nullable=False)
    # DB date created
    date_created = mapped_column(DateTime, nullable=False, default=func.now())

    def to_dict(self):
        # see OpenAPI documentation
        return { 
            'trace_id': self.trace_id,
            "customers": self.customers,
            "cookies_sold": self.cookies_sold,
            "income": self.income,
            "reported_time": datetime.strftime(self.reported_time, app_config['date_format']),
        }

