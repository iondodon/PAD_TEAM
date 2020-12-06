#!flask/bin/python
import json
import redis
import requests
from loadbalancer import LoadBalancer
from circuitbreaker import CircuitBreaker
from gateway import Gateway

from termcolor import colored


import logging
from logstash_async.handler import AsynchronousLogstashHandler
import time
from time import strftime, gmtime

from cache_driver import CacheDriver
import os
from errors_handling import CustomError

from sanic.exceptions import abort

from sanic import Sanic
from sanic import response, request
from sanic_jinja2 import SanicJinja2

from two_phase_commit import TwoPhaseCommit
from response_caching import ResponseCaching
from time import sleep
import json

# import threading
# import requests

app = Sanic(__name__)

jinja = SanicJinja2(app, autoescape=True)

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

gateway = Gateway() #TODO: make singleton if needed????    


# TODO: make it work with True!!!
SAVE_CACHE_RESPONSE = True
# SAVE_CACHE_RESPONSE = False

response_caching = ResponseCaching()




###### Define possible cache statuses#####
SUCCESS = 1 
CUSTOM_CACHE_FAILED = 2
REDIS_CACHE_FAILED = 3
BOTH_CACHES_FAILED = 4
##########################################

@app.route('/')
async def index(request):
    # test_logger.info("Hello from flask at %s", time.time())
    test_logger.info("Hello from flask at %s", strftime("%d-%m-%Y %H:%M:%S", gmtime()))

    return response.json("Hello!")


# @app.route('/test-2pc', methods=['GET', 'POST'])
@app.route('/test-2pc', methods=['POST'])
async def index(request):
    test_logger.info("Test 2 phase commit at %s", strftime("%d-%m-%Y %H:%M:%S", gmtime()))

    # data = request.data in sanic doesn't exist
    data = request.json
    print(colored("json:", "red"), request.json)
    print(colored("args:", "red"), request.args)

    
    print(colored("Test 2Phase Commit 2PC", "yellow"))

    try:
        coordinator = TwoPhaseCommit()
        res = coordinator.perform(data["service_addresses"])
        if res == "success":
            test_logger.info("2pc succeeded")
            return response.json({"status": "success", "message":"2pc succeeded"})
        else:
            test_logger.info("2pc aborted, one or more services not ready")
            return response.json({"status": "aborted", "message":"2pc aborted, one or more services not ready"})
    except:
        test_logger.error("2phase commit failed with some errors")    
        return abort(500, "2phase commit failed with some errors")

    return response.json("2pc")


@app.route('/<path>', methods=['GET', 'POST'])
async def router(request, path):    
    test_logger.info("----Request to path:" + path)
    # print(colored("----Request to path:" + path, "yellow"))

    # NOTE: RPC works only with underscore(_) request, but new feature added that gateway can process both _ and - request, so we allow both
    # TODO!!! Change request paths to custom services we use!!!
    

    if not gateway.is_path_allowed(path):
        test_logger.error("ERROR: Page not found. Path " + path + " is not in allowed paths.")
        return abort(404)

    service_type = gateway.get_service_type(path)
    

    if request.method == 'GET':
        data = request.args
        method = "GET"
    elif request.method == 'POST':
        # data = request.data
        data = request.json
        method = "POST"
        # data = request.form
    else:
        data = request.data



    if method=="GET" and response_caching.is_in_cache(path, data):
        res = response_caching.get_from_cache(path, data)
        print(colored("Get from cache:---", "magenta"), res)
        if type(res) is bytes:
            res = res.decode('utf8')
            
        return response.json(res)
    else:
        print(colored("Not in cache, make request:---", "cyan"))

        # response = requests.get(path, params=data)
        # print("-- reponse:", response.content)  
        # print(colored("-- reponse code:" + str( response.status_code), "blue"))



        r = await gateway.make_next_request(path, service_type, data, method)
        sleep(0.3)

        if "status" in r and r["status"] =="error":
            if "message" in r:
                if r["message"]=="No services available":
                    return abort(503, {"error": r["message"]})
                # else
                return abort(500, {"error": r["message"]})
            # else
            return abort(500)
        # else

        # response_caching.save_response(path, data, response.json(r))
        # response_caching.save_response(path, data, r)
        # response_caching.save_response(path, data, response.html(r))

        print(colored(">>>r:", "cyan", "on_grey"), r["response"])
            
        # !!!!!!!!!!!TODO: makw this work!!!!!!!! - response caching
        if SAVE_CACHE_RESPONSE:
            try:
                response_caching.save_response(path, data, str(r["response"]))
            except:
                test_logger.error("ERROR! couldn't save in cache response from path " + path + " with data" + str(data) + " and response: " + r)


    return response.json(r["response"])
    # return r




@app.route('/service-register', methods=['POST'])
async def service_register(request):    
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

        cache = CacheDriver()
        try:
            cache.do("redis", 'lpush', ["services-" + str(service_type), service_address])
        except Exception as e:
            test_logger.error("ERROR: Redis cache failed on command lpush at %s", strftime("%d-%m-%Y %H:%M:%S", gmtime()))
            test_logger.error(str(e))
            cache_status = REDIS_CACHE_FAILED

        try:
            cache.do("custom", 'lpush', ["services-" + str(service_type), service_address])

        except Exception as e:
            test_logger.error("ERROR: Custom cache failed on command lpush at %s", strftime("%d-%m-%Y %H:%M:%S", gmtime()))
            test_logger.error(str(e))
            cache_status = REDIS_CACHE_FAILED if SUCCESS else BOTH_CACHES_FAILED

        
        if cache_status==BOTH_CACHES_FAILED:
            test_logger.error("ERROR: Custom cache and Redis cache both failed! at %s", strftime("%d-%m-%Y %H:%M:%S", gmtime()))
            return abort(500, {"error:", "ERROR! Cache failure. Somethig went wrong"})


        test_logger.info("Service " + str(service_name) 
                                    + "of type " + str(service_type) 
                                    + " with address " + str(service_address) 
                                    + " registered!")

        return response.json({"status": "success", "message": "Service registered"})
    except Exception as e:
        test_logger.error("ERROR: Service " + str(service_name) + "  not registered. Somethig went wrong. Error:" + str(e))
        return abort(500, {"error:", "ERROR! Service not registered. Somethig went wrong"})



@app.route('/registered-services')
async def get_registered_services(request):
    result = {}

    
    # l_type1 = cache.lrange('services-type1', 0, -1)
    # l_type2 = cache.lrange('services-type2', 0, -1)
    cache = CacheDriver()
    try:
        l_type1 = cache.do("custom", 'lrange', ['services-type1', 0, -1])
        l_type2 = cache.do("custom", 'lrange', ['services-type2', 0, -1])

        if (type(l_type1) == int) or (type(l_type2) == int):
            test_logger.error("Type of l_type1 or l_type2  of custom cache should be int")
            raise CustomError("Type of l_type1 or l_type2  of custom cache should be int")
    except Exception as e:
        try:
            test_logger.error("ERROR: Custom cache lrange command failed. " + str(e))

            l_type1 = cache.do("redis", 'lrange', ['services-type1', 0, -1])
            l_type2 = cache.do("redis", 'lrange', ['services-type2', 0, -1])

            
        except Exception as e:
            test_logger.error("ERROR: Alert! Both caches failed on command lrange!!!." + str(e))
            # return abort(500, "Error: Both caches failed!")
            return response.json({"registered_services-type1": [], "registered_services-type2": [], "status": "Both caches failed so no available service for now"})


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
    return response.json({"registered_services-type1": str(result_type1), "registered_services-type2": str(result_type2)})




if __name__ == '__main__':
    gateway_port = os.environ.get("GATEWAY_PORT", 5005)
    app.run(host='0.0.0.0', debug=True, port=gateway_port)