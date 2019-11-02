from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
load_dotenv()

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

app = Flask(__name__)

from .views import *

if __name__ == '__main__':
    app.run()
