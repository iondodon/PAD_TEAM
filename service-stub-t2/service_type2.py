
from sanic import Sanic
from sanic import response
from sanic_jinja2 import SanicJinja2

import json

import threading
import requests
import os

app = Sanic(__name__)

jinja = SanicJinja2(app, autoescape=True)

@app.listener('before_server_start')
def register_myself(sanic, loop):
    try:    
        my_address = os.environ.get("SERVICE_MY_ADDRESS", 'http://localhost:8001')

        params = {
            "address": my_address + "/",
            "type":"type2", 
            "service_name": "service-stub-t2"
        }

        gateway_address = os.environ.get('GATEWAY_ADDRESS', 'http://localhost:5003')
        if gateway_address[-1]!= "/":
            gateway_address += "/"

        gateway_address += 'service-register'

        r = requests.post(gateway_address, json=params)

        if r.status_code == 200:
            print('Server started, quiting start_loop')
            not_started = False
        print(r.status_code)
        print(r.json())
    except Exception as e:
        print("exception:", e)
        print('Server not yet started')


@app.route('/')
async def index(request):
    return response.json({"server status": "up and running", "message":"Hello!"})


@app.route('/test-route-t2')
async def test_route(request):
    return response.json("Hello test from service of type 2!")


if __name__ == '__main__':    
    app.run(host='0.0.0.0', port=8001, debug=True)