from errors_handling import CustomError, CustomError
import requests
from termcolor import colored
from jsonrpcclient import request as rpc_request
import json
from flask import abort

import logging
from logstash_async.handler import AsynchronousLogstashHandler


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


class CircuitBreaker:
    FAILURE_THRESHOLD = 3
    # TYPE_REQUESTS = 'RPC'  # this can be 'RPC' or 'HTTP'
    TYPE_REQUESTS = 'HTTP'  # this can be 'RPC' or 'HTTP'
    # TYPE_REQUESTS = 'haha'  # should return error

    def __init__(self, address, service_type):
        self.address = address
        self.tripped = False
        self.service_type = service_type


    def request(self, redis_cache, params, method):

        redis_cache = CacheDriver('redis')

        if self.TYPE_REQUESTS not in ['RPC', 'HTTP']:
            test_logger.error("ERROR: TYPE_REQUESTS parameter '" + self.TYPE_REQUESTS +"' in circuitbreaker.py!!! not recognized."
                + "Please set TYPE_REQUESTS to 'HTTP' or 'RPC' in class CircuitBreaker")

            return abort(500, {"error": "Please set TYPE_REQUESTS to 'HTTP' or 'RPC' in circuitbreaker!!!"})
        

        if self.tripped:
            remove_from_cache(redis_cache)
            raise CustomError("Circuit breaker tripped")
            # 503 - service unavailable
            test_logger.error("ERROR: CircuitBreaker tripped. No services available")
            return abort(503, {"error": "No services available"})
            # return {"status": "error", "message":"Circuit breaker tripped"}

        endpoint = str(self.address.decode("utf-8") ) + str(params["path"]).replace("/", "")

        print(colored("service endpoint:---" + endpoint, "cyan"))

        last_error = ""

        try:
            if self.TYPE_REQUESTS == 'RPC':
                test_logger.info("Request type: RPC")
                print(colored("---RPC", "blue"))

                route = str(params["path"]).replace("/", "").replace("-", "_")
                print("-> route:", route)
                r = rpc_request(str(self.address.decode("utf-8")), route).data.result

                print(colored("Response from service:----", "green"), r)
                print(colored("Response from service decoded:----", "green"), json.loads(r))
                return  json.loads(r)

            elif self.TYPE_REQUESTS == 'HTTP':
                test_logger.info("Request type: HTTP")
                print("---HTTP")

                if method=='GET':
                    # r = requests.get(endpoint, params=params["parameters"].decode("utf-8"))
                    r = requests.get(endpoint, params=params["parameters"])
                elif method=='POST':
                    # r = requests.post(endpoint, data=params["parameters"].decode("utf-8"), json=params["parameters"].decode("utf-8"))
                    r = requests.post(endpoint, data=params["parameters"], json=params["parameters"])
                elif method=='PUT':
                    # r = requests.put(endpoint, data=params["parameters"].decode("utf-8"), json=params["parameters"].decode("utf-8"))
                    r = requests.put(endpoint, data=params["parameters"], json=params["parameters"])
                elif method=='DELETE':
                    r = requests.delete(endpoint)

                test_logger.debug("Request: " + str(r))
                print(r)    
                data = r.json()
                
                test_logger.debug("Data: " + str(data))
                print(data)
                
                test_logger.debug("Response from service:" + str(r.json()))
                print(colored("Response from service:----", "green"), r.json())

                return r.json()
                       
        except Exception as e:

            # nr_requests_failed = redis_cache.incr(self.get_redis_key())
            nr_requests_failed = redis_cache.do('incr', [self.get_redis_key()])

            test_logger.error("ERROR: Request failed. " + str(e))
            print(colored("----Request failed:----", "red"), nr_requests_failed)
            print(e)

            last_error = str(e)


        if nr_requests_failed >= self.FAILURE_THRESHOLD:
            self.remove_from_cache(redis_cache)
            self.tripped = True


        # return {"status":"error", "message": "Request to service failed", "error":last_error}
        test_logger.error("ERROR: Request to service of type " + str(self.service_type) + " failed")
        return abort(500, {"message":"Request to service failed", "error ":last_error})


    def clear(self, address):
        self.address = None


    def get_redis_key(self):
        return "circuit_breaker:" + self.address.decode('utf-8')


    def remove_from_cache(self, redis_cache):
        print(colored("Remove service from cache:", "yellow"), self.address)
        test_logger.info("Remove service from cache: " + str(self.address))

        redis_cache.do('lrem', ["services-"+str(self.service_type), 1, self.address])
        redis_cache.do('delete', [self.get_redis_key()])
        # redis_cache.lrem("services-"+str(self.service_type), 1, self.address)
        # redis_cache.delete(self.get_redis_key())
