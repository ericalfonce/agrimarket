import os

class Config:
    SECRET_KEY = "same-secret-key-on-both-servers"

    DB_NAME = "agrimarket"
    DB_USER = "agrimarket_user"
    DB_PASSWORD = "yourpassword"
    DB_HOST = "localhost"
    DB_PORT = 5432
