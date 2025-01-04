from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///warehouse.db")
Base.metadata.create_all(engine)
SessionFactory = sessionmaker(bind=engine)
