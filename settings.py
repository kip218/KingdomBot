from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
TOKEN = os.getenv('TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')