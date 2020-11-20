from errors_handling import CustomError, CustomError
import requests
from termcolor import colored
from jsonrpcclient import request as rpc_request
import json
from flask import abort


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

        if self.TYPE_REQUESTS not in ['RPC', 'HTTP']:
            return abort(500, {"error": "Please set TYPE_REQUESTS to 'HTTP' or 'RPC' in circuitbreaker!!!"})
        

        if self.tripped:
            remove_from_cache(redis_cache)
            raise CustomError("Circuit breaker tripped")
            # 503 - service unavailable
            return abort(503, {"error": "No services available"})
            # return {"status": "error", "message":"Circuit breaker tripped"}

        endpoint = str(self.address.decode("utf-8") ) + str(params["path"]).replace("/", "")
        print(colored("service endpoint:---" + endpoint, "cyan"))

        last_error = ""

        try:
            if self.TYPE_REQUESTS == 'RPC':
                print(colored("---RPC", "blue"))
                route = str(params["path"]).replace("/", "").replace("-", "_")
                print("-> route:", route)
                r = rpc_request(str(self.address.decode("utf-8")), route).data.result

                print(colored("Response from service:----", "green"), r)
                print(colored("Response from service decoded:----", "green"), json.loads(r))
                return  json.loads(r)

            elif self.TYPE_REQUESTS == 'HTTP':
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

                print(r)    
                data = r.json()
                print(data)
                print(colored("Response from service:----", "green"), r.json())
                return r.json()
                       
        except Exception as e:

            nr_requests_failed = redis_cache.incr(self.get_redis_key())

            print(colored("----Request failed:----", "red"), nr_requests_failed)
            print(e)

            last_error = str(e)


        if nr_requests_failed >= self.FAILURE_THRESHOLD:
            self.remove_from_cache(redis_cache)
            self.tripped = True


        # return {"status":"error", "message": "Request to service failed", "error":last_error}
        return abort(500, {"message":"Request to service failed", "error ":last_error})


    def clear(self, address):
        self.address = None


    def get_redis_key(self):
        return "circuit_breaker:" + self.address.decode('utf-8')


    def remove_from_cache(self, redis_cache):
        print(colored("Remove service from cache:", "yellow"), self.address)
        redis_cache.lrem("services-"+str(self.service_type), 1, self.address)
        redis_cache.delete(self.get_redis_key())
