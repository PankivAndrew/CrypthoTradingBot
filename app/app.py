from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
from threading import Thread
load_dotenv()

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

app = Flask(__name__)

from .views import *
from .predictions import start_trade

thread = Thread(target=start_trade)
thread.start()

if __name__ == '__main__':
    app.run()
    thread.join()
