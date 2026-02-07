import psycopg2
from flask import g
from config import Config

def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            host=Config.DB_HOST,
            port=Config.DB_PORT
        )
    return g.db
