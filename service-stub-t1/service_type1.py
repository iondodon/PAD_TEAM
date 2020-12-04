
from sanic import Sanic
from sanic import response
from sanic_jinja2 import SanicJinja2

import json

import threading
import requests

app = Sanic(__name__)

jinja = SanicJinja2(app, autoescape=True)

@app.listener('before_server_start')
def register_myself(sanic, loop):
    try:
        # r = requests.get('http://127.0.0.1:5000/')
        # r = requests.get('http://localhost:5003/registered-services')
        
        my_address = 'http://192.168.0.20' + ':8000'
        # my_address = 'http://0.0.0.0:8000'

        params = {
            "address": my_address + "/",
            "type":"type1", 
            "service_name": "service-stub-t1"
        }

        r = requests.post('http://localhost:5003/service-register', json=params)

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


@app.route('/test-route')
async def index(request):
    return response.json("Hello test!")


if __name__ == '__main__':    
    # app.run(host='127.0.0.1', port=8000, debug=True)
    # 0.0.0.0 accesibil din retea
    
    app.run(host='0.0.0.0', port=8000, debug=True)