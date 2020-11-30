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
from time import strftime, gmtime

from cache_driver import CacheDriver
import os

app = Flask(__name__)
# if this is set to false and in docker flask_env is not development, the "debug" logging will not be shown
app.config['DEBUG'] = True



# Setup elk stack
# host_logger = 'localhost'
host_logger = 'logstash'
port_logger = 5000

# Get you a test logger
test_logger = logging.getLogger('python-logstash-logger')
# Set it to whatever level you want - default will be info
test_logger.setLevel(logging.DEBUG)
# Create a handler for it
async_handler = AsynchronousLogstashHandler(host_logger, port_logger, database_path=None)
# Add the handler to the logger
test_logger.addHandler(async_handler)

# Initialize load balancer
load_balancer = LoadBalancer()


###### Define possible cache statuses#####
SUCCESS = 1
CUSTOM_CACHE_FAILED = 2
REDIS_CACHE_FAILED = 3
BOTH_CACHES_FAILED = 4
##########################################

@app.route('/')
def index():
    # test_logger.info("Hello from flask at %s", time.time())
    test_logger.info("Hello from flask at %s", strftime("%d-%m-%Y %H:%M:%S", gmtime()))

    return "Hello!"

@app.route('/<path>', methods=['GET', 'POST'])
def router(path):    
    test_logger.info("----Request to path:" + path)
    # print(colored("----Request to path:" + path, "yellow"))

    # NOTE: RPC works only with underscore(_) request, but new feature added that gateway can process both _ and - request, so we allow both
    # TODO!!! Change request paths to custom services we use!!!
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
        test_logger.error("ERROR: Page not found. Path " + path + " is not in allowed paths.")
        return abort(404)


    service_type = map_service_type_paths[path]

    if path == "s1-status":
        path = "status"
        service_type = "type1"
    elif path == "s2-status":
        path = "status"
        service_type = "type2"

    if not load_balancer.any_available(service_type):
        # 503 Service Unavailable
        test_logger.error("ERROR: No service of type " + service_type + " available")
        return abort(503, {"error": "No services available"})

    if request.method == 'GET':
        data = request.args
    elif request.method == 'POST':
        data = request.data
        # data = request.form
    else:
        data = request.data

    # print("DATA", data)
    test_logger.debug("Request data: " + str(data))

    parameters = {
        # "path": request.path,
        "path": path,
        "parameters": data
    }

    test_logger.debug("Parameters " + str(parameters))
    # print(colored("parameters:", "magenta"), parameters)

    circuit_breaker = load_balancer.next(service_type)
    service_response = circuit_breaker.request(parameters, request.method)

 
    return service_response


@app.route('/service-register', methods=['POST'])
def service_register():    
    # print(request.data)
    # print(request.json)
    test_logger.info("Service discovered!")
    # print("Service discovered!")

    service_name = request.json["service_name"]
    service_address = request.json["address"]
    service_type = request.json["type"]

    if service_type not in ["type1", "type2"]:
        # return {"status":"error", "message": "service_type should be type1 or type2"}
        # 400 bad request
        test_logger.error("ERROR: Service type " + str(service_type) + " not recognized. Service type should be type1 or type2")
        return abort(400, {"error": "service_type should be type1 or type2"})

    test_logger.debug("service name: " + str(service_name))
    test_logger.debug("service address: " + str(service_address))
    test_logger.debug("service type: " + str(service_type))
    # print(colored("service name:", "red"), service_name)
    # print(colored("service address:", "red"), service_address)
    # print(colored("service type:", "red"), service_type)
    
    #################################
    # TODO: test and add in cache - last time up, pentru alte requesturi de ex. get, verifici daca rezultatele sunt diferite
    # la ambele cache-uri, atunci vezi care din ele a fost mai recent up si inseamna ca il sincronizezi cu celelalt
    # TODO: de modificat dupa acest model sa lucreze peste tot unde este cache!! (active-active replication)
    try:
        # cache = CacheDriver('redis')
        cache_status = SUCCESS

        try:
            redis_cache = CacheDriver('redis')
            redis_cache.do('lpush', ["services-" + str(service_type), service_address])
        except:
            test_logger.error("ERROR: Redis cache failed on command lpush at %s", strftime("%d-%m-%Y %H:%M:%S", gmtime()))
            cache_status = REDIS_CACHE_FAILED

        try:
            cache = CacheDriver('custom')
            cache.do('lpush', ["services-" + str(service_type), service_address])
        except:
            test_logger.error("ERROR: Custom cache failed on command lpush at %s", strftime("%d-%m-%Y %H:%M:%S", gmtime()))
            if cache_status=="success":
                cache_status = CUSTOM_CACHE_FAILED
            else:
                cache_status = ALL_CACHES_FAILED
                test_logger.error("ERROR: Custom cache and Redis cache both failed! at %s", strftime("%d-%m-%Y %H:%M:%S", gmtime()))
                return abort(500, {"error:", "ERROR! Cache failure. Somethig went wrong"})

        

        test_logger.info("Service " + str(service_name) 
                                    + "of type " + str(service_type) 
                                    + " with address " + str(service_address) 
                                    + " registered!")
        return {"status": "success", "message": "Service registered"}
    except:
        test_logger.error("ERROR: Service " + str(service_name) + "  not registered. Somethig went wrong")
        return abort(500, {"error:", "ERROR! Service not registered. Somethig went wrong"})



@app.route('/registered-services')
def get_registered_services():
    result = {}

    try:
        redis_cache = CacheDriver('redis')
    except:
        test_logger.error("ERROR: Redis cache initialization failed")
    try:
        cache = CacheDriver('custom')
    except:
        test_logger.error("ERROR: Custom cache initialization failed")

    # l_type1 = cache.lrange('services-type1', 0, -1)
    # l_type2 = cache.lrange('services-type2', 0, -1)
    try:
        l_type1 = cache.do('lrange', ['services-type1', 0, -1])
        l_type2 = cache.do('lrange', ['services-type2', 0, -1])
    except:
        test_logger.error("ERROR: Custom cache lrange command failed")

        l_type1 = redis_cache.do('lrange', ['services-type1', 0, -1])
        l_type2 = redis_cache.do('lrange', ['services-type2', 0, -1])

    print(colored('--l_type1:', 'blue'), l_type1)
    print(colored('type l_type1:', 'blue'), type(l_type1))
    print(colored('--l_type2:', 'blue'), l_type2)
    print(colored('type l_type2:', 'blue'), type(l_type2))

    result_type1 = []
    result_type2 = []

    if l_type1:    
        result_type1 = [x for x in l_type1]

    if l_type2:
        result_type2 = [x for x in l_type2]

    test_logger.info({"registered_services-type1": str(result_type1), "registered_services-type2": str(result_type2)})
    return {"registered_services-type1": str(result_type1), "registered_services-type2": str(result_type2)}




if __name__ == '__main__':
    gateway_port = os.environ.get("GATEWAY_PORT", 5005)
    app.run(host='0.0.0.0', debug=True, port=gateway_port)