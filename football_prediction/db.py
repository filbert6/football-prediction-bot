import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class ModelMetadata(Base):
    __tablename__ = "model_metadata"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    version = Column(String, nullable=True)
    metrics = Column(JSON, nullable=True)
    trained_at = Column(DateTime, default=datetime.utcnow)


class BacktestResult(Base):
    __tablename__ = "backtest_result"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_engine(database_url=None):
    database_url = database_url or os.environ.get("DATABASE_URL", "sqlite:///./football_prediction.db")
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    return engine


def init_db(engine=None):
    engine = engine or get_engine()
    Base.metadata.create_all(engine)
    return engine


def get_session(engine=None):
    engine = engine or get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def save_model_metadata(session, name, path, version=None, metrics=None):
    m = ModelMetadata(name=name, path=path, version=version, metrics=metrics)
    session.add(m)
    session.commit()
    return m


def save_backtest(session, name, metrics):
    b = BacktestResult(name=name, metrics=metrics)
    session.add(b)
    session.commit()
    return b
