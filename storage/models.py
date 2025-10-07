from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer, String, DateTime, func, Float
from datetime import datetime

date_format = "%Y-%m-%d %H:%M:%S"


class Base(DeclarativeBase):
    pass

class Ridership(Base):
    __tablename__ = "ridership"
    id = mapped_column(Integer, primary_key=True)
    # ?
    trace_id = mapped_column(String(36), nullable=False)
    bus_id = mapped_column(String(36), nullable=False)
    route_name = mapped_column(String(7), nullable=False)
    stop_id = mapped_column(Integer, nullable=False)
    passengers_boarded = mapped_column(Integer, nullable=False)
    recorded_timestamp = mapped_column(DateTime, nullable=False)
    batch_timestamp = mapped_column(DateTime, nullable=False)
    # DB date created
    date_created = mapped_column(DateTime, nullable=False, default=func.now())

    def to_dict(self):
        # see OpenAPI documentation
        return { 
            'trace_id': self.trace_id,
            "bus_id": self.bus_id,
            "route_name": self.route_name,
            "stop_id": self.stop_id,
            "passengers_boarded": self.passengers_boarded,
            "recorded_timestamp": datetime.strftime(self.recorded_timestamp, date_format),
            "batch_timestamp": datetime.strftime(self.batch_timestamp, date_format)
        }

class Fuel(Base):
    __tablename__ = "fuel"
    id = mapped_column(Integer, primary_key=True)
    # ?
    trace_id = mapped_column(String(36), nullable=False)
    bus_id = mapped_column(String(36), nullable=False)
    route_name = mapped_column(String(7), nullable=False)
    fuel_litres = mapped_column(Float, nullable=False)
    recorded_timestamp = mapped_column(DateTime, nullable=False)
    batch_timestamp = mapped_column(DateTime, nullable=False)
    # DB date created
    date_created = mapped_column(DateTime, nullable=False, default=func.now())

    def to_dict(self):
        # see OpenAPI documentation
        return { 
            'trace_id': self.trace_id,
            "bus_id": self.bus_id,
            "route_name": self.route_name,
            "fuel_litres": self.fuel_litres,
            "recorded_timestamp": datetime.strftime(self.recorded_timestamp, date_format),
            "batch_timestamp": datetime.strftime(self.batch_timestamp, date_format)
        }
