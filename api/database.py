import os
import psycopg2


def get_connection():
    dsn = os.environ['DATABASE_URL']
    return psycopg2.connect(dsn)
