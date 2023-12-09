import os
import psycopg2
from dotenv import load_dotenv


try:
    load_dotenv()
    conn = psycopg2.connect(
        dbname=os.environ.get('POSTGRES_NAME'),
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD'),
        host=os.environ.get('POSTGRES_HOST'),
        port=os.environ.get('POSTGRES_PORT')
    )
    cursor = conn.cursor()
    print("Successfully connected")
except psycopg2.Error as e:
    print("Failed to establish a connection: ", e)