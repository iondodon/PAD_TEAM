from errors_handling import CustomError
from termcolor import colored
# from jsonrpcclient import request as rpc_request
# import json
from flask import abort
from loadbalancer import LoadBalancer

import logging
from logstash_async.handler import AsynchronousLogstashHandler
from sanic import response

# from cache_driver import CacheDriver


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


class Gateway:
    MAX_RETRIES = 5

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
        "status" : "",

        "test-route": "type1",
        "test-route-t2": "type2"
    }

    def __init__(self):
        # TODO; test
        self.load_balancer = LoadBalancer()

    def is_path_allowed(self, path):
        allowed_paths = self.map_service_type_paths.keys()

        return path in allowed_paths

    def get_service_type(self, path):
        service_type = self.map_service_type_paths[path]

        if path == "s1-status":
            path = "status"
            service_type = "type1"
        elif path == "s2-status":
            path = "status"
            service_type = "type2"

        return service_type


    async def make_next_request(self, path, service_type, data, method, counter=0):
        if not self.load_balancer.any_available(service_type):
            # 503 Service Unavailable
            test_logger.error("ERROR: No service of type " + service_type + " available")
            return abort(503, {"error": "No services available"})

        # print("DATA", data)
        test_logger.debug("Request data: " + str(data))

        parameters = {
            # "path": request.path,
            "path": path,
            "parameters": data
        }

        test_logger.debug("Parameters " + str(parameters))
        # print(colored("parameters:", "magenta"), parameters)

        circuit_breaker = self.load_balancer.next(service_type)

        if circuit_breaker is None:
            return abort(500, {"error": "Server error in load_balancer.next(...) method. No services found in cache."})

        service_response = await circuit_breaker.request(parameters, method)

        if service_response["status"] == "success": 
            return response.json(service_response["response"])

        # if service_response["status"] == "error" and service_response["message"] == "Circuit Breaker Tripped":
        if service_response["status"] == "error":

            if counter < self.MAX_RETRIES:
                counter += 1
                return await self.make_next_request(path, service_type, data, method, counter)
            # else
            if "message" in service_response:
                return abort(500, {"error": service_response["message"]})
            # else:
            return abort(500)
        
        return abort(500, {"error": "Error in request to service"})
