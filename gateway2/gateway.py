#!flask/bin/python
from flask import Flask
from flask import request, abort
import json
import redis
import requests
from loadbalancer import LoadBalancer
from circuitbreaker import CircuitBreaker
from termcolor import colored


import logging
from logstash_async.handler import AsynchronousLogstashHandler
import time

app = Flask(__name__)
# app.config['FLASK_ENV'] = "development"
app.config['DEBUG'] = True



# Setup elk stack
# host_logger = 'localhost'
host_logger = 'logstash'
# host_logger = 'elk'
port_logger = 5000

# Get you a test logger
test_logger = logging.getLogger('python-logstash-logger')
# Set it to whatever level you want - default will be info
test_logger.setLevel(logging.DEBUG)
# Create a handler for it
async_handler = AsynchronousLogstashHandler(host_logger, port_logger, database_path=None)
# Add the handler to the logger
test_logger.addHandler(async_handler)


# Setup Redis cache
redis_cache = redis.Redis(host='redis', port=6379, db=0)
load_balancer = LoadBalancer()



@app.route('/')
def index():
    test_logger.info("Hello from flask at %s", time.time())
    return "Hello!"

@app.route('/<path>', methods=['GET', 'POST'])
def router(path):    
    test_logger.info("----Request to path:" + path)
    
    print(colored("----Request to path:" + path, "yellow"))
    # NOTE: RPC works only with underscore(_) request, but new feature added that gateway can process both _ and - request, so we allow both
    map_service_type_paths = {
        "init-student" : "type1",
        "init_student" : "type1",
        "nota" : "type1",
        "nota-atestare" : "type1",
        "nota_atestare" : "type1",

        "nota-examen" : "type2",
        "nota_examen" : "type2",
        "pune-nota_atestare" : "type2",
        "pune_nota_atestare" : "type2",
        "nota-finala": "type2",
        "nota_finala": "type2",
        "get-all-exam-marks": "type2",
        "get-all-midterm-marks": "type2",
        "s2-nota-atestare": "type2",
        "s2-validate-student-marks":"type2",


        "s2-status": "type2",
        "s1-status": "type1",
        "status" : ""
    }

    allowed_paths = map_service_type_paths.keys()

    if path not in allowed_paths:
        test_logger.error("Page not found. Path " + path + " is not in allowed paths.")
        return abort(404)


    service_type = map_service_type_paths[path]

    if path == "s1-status":
        path = "status"
        service_type = "type1"
    elif path == "s2-status":
        path = "status"
        service_type = "type2"

    if not load_balancer.any_available(redis_cache, service_type):
        # 503 Service Unavailable
        test_logger.error("No service of type " + service_type + " available")
        return abort(503, {"error": "No services available"})

    if request.method == 'GET':
        data = request.args
    elif request.method == 'POST':
        data = request.data
        # data = request.form
    else:
        data = request.data

    print("DATA", data)

    parameters = {
        # "path": request.path,
        "path": path,
        "parameters": data
    }

    print(colored("parameters:", "magenta"), parameters)

    circuit_breaker = load_balancer.next(redis_cache, service_type)
    service_response = circuit_breaker.request(redis_cache, parameters, request.method)

 
    return service_response


@app.route('/service-register', methods=['POST'])
def service_register():    
    print(request.data)
    print(request.json)
    print("Service discovered!")

    service_name = request.json["service_name"]
    service_address = request.json["address"]
    service_type = request.json["type"]

    if service_type not in ["type1", "type2"]:
        # return {"status":"error", "message": "service_type should be type1 or type2"}
        # 400 bad request
        test_logger.error("Service type " + str(service_type) + " not recognized. Service type should be type1 or type2")
        return abort(400, {"error": "service_type should be type1 or type2"})

    print(colored("service name:", "red"), service_name)
    print(colored("service address:", "red"), service_address)
    print(colored("service type:", "red"), service_type)
    
    try:
        redis_cache.lpush("services-" + str(service_type), service_address)

        return {"status": "success", "message": "Service registered"}
    except:
        test_logger.error("Service " + str(service_name) + "  not registered. Somethig went wrong")
        return abort(500, {"error:", "ERROR! Service not registered. Somethig went wrong"})



@app.route('/registered-services')
def get_registered_services():
    result = {}

    l_type1 = redis_cache.lrange('services-type1', 0, -1)
    l_type2 = redis_cache.lrange('services-type2', 0, -1)
    
    result_type1 = [x for x in l_type1]
    result_type2 = [x for x in l_type2]

    test_logger.info({"registered_services-type1": str(result_type1), "registered_services-type2": str(result_type2)})
    return {"registered_services-type1": str(result_type1), "registered_services-type2": str(result_type2)}




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5003)