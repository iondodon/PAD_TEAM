import grequests
from termcolor import colored
import time
import uuid
from cache_driver import CacheDriver
import os


USE_LOGGER = os.environ.get("USE_LOGGER", False)
USE_LOGGER = False


if USE_LOGGER:
    import logging
    from logstash_async.handler import AsynchronousLogstashHandler

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



###### Define possible cache statuses#####
SUCCESS = 1
CUSTOM_CACHE_FAILED = 2
REDIS_CACHE_FAILED = 3
BOTH_CACHES_FAILED = 4
##########################################


class TwoPhaseCommit():
    
    def create_transaction(self):
        """generates transaction id (unique) and saves it in cache in active_transactions key"""

        print(colored("--Create transaction started--", "blue"))
        transaction_id = uuid.uuid4()
        self.tid  = transaction_id
        print(colored("--transaction id--", "blue"), transaction_id)

        cache = CacheDriver()

        try:
            cache.do("redis", 'lpush', ["active_transactions" + str(self.tid)])
        except Exception as e:
            if USE_LOGGER:
                test_logger.error("ERROR: Redis cache failed on command lpush at %s", strftime("%d-%m-%Y %H:%M:%S", gmtime()))
                test_logger.error(str(e))

            cache_status = cache_FAILED
            print(colored("ERROR: Redis cache failed on command lpush at %s" + strftime("%d-%m-%Y %H:%M:%S", gmtime()), "red"))

        try:
            cache.do("custom", 'lpush', ["active_transactions" + str(self.tid)])

        except Exception as e:
            if USE_LOGGER:
                test_logger.error("ERROR: Custom cache failed on command lpush at %s", strftime("%d-%m-%Y %H:%M:%S", gmtime()))
                test_logger.error(str(e))
            print(colored("ERROR: Custom cache failed on command lpush at %s" + strftime("%d-%m-%Y %H:%M:%S", gmtime()), "red"))

            cache_status = cache_FAILED if SUCCESS else BOTH_CACHES_FAILED

        
        if cache_status==BOTH_CACHES_FAILED:
            if USE_LOGGER:
                test_logger.error("ERROR: Custom cache and Redis cache both failed! at %s", strftime("%d-%m-%Y %H:%M:%S", gmtime()))
            print(colored("ERROR: Custom cache and Redis cache both failed! at %s" +strftime("%d-%m-%Y %H:%M:%S", gmtime()), "red"))

        return self.tid


    def prepare_transaction(self, service_addresses, parameters={}):
        """ prepare transaction by sending requests to each service from service_addresses list"""
        print(colored("--Prepare transaction started --", "blue"))

        hasSuccess = True

        parameters["tid"] = self.tid

        requests_list = []
        for address in service_addresses:
            endpoint = address + "/prepare_transaction"
            r = grequests.get(endpoint, params=parameters)
            requests_list.append(r)

        try:
            rs = grequests.map([r], exception_handler=self.exception_handler)
            for response in rs:
                print("-> response:", response)
                if response is None or response.json() != "prepared":  #TODO
                    hasSuccess = False

        except Exception as e:
            hasSuccess = False
            print("Exception: " + str(e))
            if USE_LOGGER:
                test_logger.error("Exception: " + str(e))

        return hasSuccess #returns true or false if all services from list are prepared


    def commit_transaction(self, service_addresses, parameters={}):
        """ commit transaction by sending requests to each service from service_addresses list"""
        print(colored("--Commit transaction started--", "yellow"))

        hasSuccess = True

        parameters["tid"] = self.tid

        requests_list = []
        for address in service_addresses:
            endpoint = address + "/commit_transaction"
            r = grequests.get(endpoint, params=parameters)
            requests_list.append(r)

        try:
            rs = grequests.map([r], exception_handler=self.exception_handler)
            for response in rs:
                print("-> response:", response)
                if USE_LOGGER:
                    test_logger.info("-> response:", response)

                if response is None or response.json() != "success":  #TODO
                    hasSuccess = False

        except Exception as e:
            hasSuccess = False

            print("Exception: " + str(e))
            if USE_LOGGER:
                test_logger.error("Exception: " + str(e))

        return hasSuccess


    def abort_transaction(self, service_addresses):
        """ abort transaction by sending requests to each service from service_addresses list"""
        print(colored("--Abort transaction started--", "red"))

        parameters = {}
        parameters["tid"] = self.tid

        requests_list = []
        for address in service_addresses:
            endpoint = address + "/abort_transaction"
            r = grequests.get(endpoint, params=parameters)
            requests_list.append(r)

        try:
            rs = grequests.map([r], exception_handler=self.exception_handler)
            for response in rs:
                print("-> response:", response)
                test_logger.info("-> response:", response)

                if response is None or response.json() != "success":  #TODO sau de verificat daca status nu e 200
                    if USE_LOGGER:
                        test_logger.error("Error! Abort transaction failed")
                    return {"status": "error", "message": "abort transaction failed"}

        except Exception as e:
            hasSuccess = False
            
            print("Exception: " + str(e))
            if USE_LOGGER:
                test_logger.error("Error! Abort transaction failed with exception: " + str(e))

            return {"status": "error", "message": "abort transaction failed"}

        return {"status": "success", "message": "abort transaction succeeded"}


    def end_transaction(self):
        """ end transaction by removing transaction_id tid from 'active_transactions' from cache"""
        print(colored("--End transaction started--", "blue"))

        return self.remove_tid_from_cache()


    def remove_tid_from_cache(self):
        """ remove transaction_id from active_transactions from cache"""
        cache_status = SUCCESS

        cache = CacheDriver()
        try:
            cache.do("custom", 'lrem', ["active_transactions", self.tid])
        except Exception as e:
            colored("ERROR: Custom cache lrem command failed on key " + "active_transactions", "red")

            if USE_LOGGER:
                test_logger.error("ERROR: Custom cache lrem command failed on key " + "active_transactions")
                test_logger.error(str(e))
            cache_status = CUSTOM_CACHE_FAILED

        try:
            cache.do("redis", 'lrem', ["active_transactions", self.tid])
        except Exception as e:
            print(colored("ERROR: Redis cache lrem command failed on key " + "'active_transactions'", "red"))

            if USE_LOGGER:
                test_logger.error("ERROR: Redis cache lrem command failed on key " + "'active_transactions'")
                test_logger.error(e)
            cache_status = REDIS_CACHE_FAILED if SUCCESS else BOTH_CACHES_FAILED

        if cache_status == BOTH_CACHES_FAILED:
            print(colored("ERROR: Redis cache lrem command failed on key " + "'active_transactions'", "red"))
            if USE_LOGGER:
                test_logger.error("ERROR: Alert! Both caches failed on lrem command on key " + "'active_transactions'")

        if cache_status==SUCCESS:
            return "success"
        return "error"


    def perform(self, service_addresses, parameters={}):
        status = "error"
        try:    
            self.create_transaction()
        except:
            status =  "error"

        try:
            status_prepared = self.prepare_transaction(service_addresses, parameters)
            
            print(colored("--Is transaction prepared?--", "blue"), status_prepared)

            if status_prepared==True:
                if self.commit_transaction(service_addresses, parameters):
                    status = "success"
            else:
                if self.abort_transaction(service_addresses):
                    status = "aborted"
                else:
                    status = "error"
        except:
            status =  "error"

        try:
            self.end_transaction()
        except:
            status =  "error"

        return status


    def exception_handler(self, request, exception):
        """ handle exceptions from grequests requests """

        print(colored("Request failed", "red"))
        print(colored("--request:", "red"), request)
        print(colored("--exception:", "red"), exception)

        if USE_LOGGER:
            test_logger.error("ERROR! Request failed on request:" + str(request))
            test_logger.error("Exception:" + str(exception))
            


