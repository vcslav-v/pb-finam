from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os import environ

if environ.get('DATABASE_URL'):
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL').replace(
        'postgres', 'postgresql+psycopg2'
    )
else:
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:mysecretpassword@0.0.0.0/postgres'

engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
