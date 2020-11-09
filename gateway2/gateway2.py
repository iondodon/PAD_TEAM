from flask import Flask
from flask import request, abort
import json
# import redis
# import requests
# from loadbalancer import LoadBalancer
# from circuitbreaker import CircuitBreaker
# from termcolor import colored


import logging
from logstash_async.handler import AsynchronousLogstashHandler
import time

# Setup elk stack
host_logger = 'localhost'
port_logger = 5000

# Get you a test logger
test_logger = logging.getLogger('python-logstash-logger')
# Set it to whatever level you want - default will be info
test_logger.setLevel(logging.DEBUG)
# Create a handler for it
async_handler = AsynchronousLogstashHandler(host_logger, port_logger, database_path=None)
# Add the handler to the logger
test_logger.addHandler(async_handler)


app = Flask(__name__)

@app.route('/')
def index():
    test_logger.info("Hello from flask at %s", time.time())
    return "Hello!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5003)