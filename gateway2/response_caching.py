import os
from cache_driver import CacheDriver
from termcolor import colored

from time import sleep

USE_LOGGER = os.environ.get("USE_LOGGER", False)


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


# TODO: make singleton??!
class ResponseCaching():
    delta_expire = 20 # save request in cache for delta seconds

    def __init__(self):
        self.cache = CacheDriver()

    def save_response(self, url, parameters, response):
        cache_status = SUCCESS
        err_prefix = "ERROR: ResponseCaching: save_response() "

        cache = self.cache

        key = "response_cached:" + url + "|" + "p:" + str(parameters) 
        value = response
        # value = "p:" + str(parameters) + "|" + response

        try:
            cache.do("redis", 'set', [key, value])
            sleep(0.4)
            cache.do("redis", 'expire', [key, self.delta_expire])
        except Exception as e:
            if USE_LOGGER:
                test_logger.error(err_prefix + "Redis cache failed on command SET & EXPIRE key: " + key + " value: " + value)
                test_logger.error(str(e))
            cache_status = REDIS_CACHE_FAILED

        try:
            cache.do("custom", 'set', [key, value])
            sleep(0.4)
            cache.do("custom", 'expire', [key, self.delta_expire])
        except Exception as e:
            if USE_LOGGER:
                test_logger.error(err_prefix + "Custom cache failed on command SET & EXPIRE key: " + key + " value: " + value)
                test_logger.error(str(e))
            cache_status = REDIS_CACHE_FAILED if SUCCESS else BOTH_CACHES_FAILED

        
        if cache_status==BOTH_CACHES_FAILED:
            if USE_LOGGER:
                test_logger.error(err_prefix + "Custom cache and Redis cache both failed! SET key: " + key + " value: " + value)

            return "error"

        if cache_status==SUCCESS:
            return "success"

        return "error"


    def is_in_cache(self, url, parameters={}):
        cache_status = SUCCESS
        err_prefix = "ERROR: ResponseCaching: is_in_cache() "

        cache = self.cache

        # key = "response_cached:" + url
        key = "response_cached:" + url + "|" + "p:" + str(parameters) 

        ttl1 = 0
        ttl2 = 0

        try:
            # cache.do("redis", 'GET', [key])
            # get time to live
            ttl1 = cache.do("redis", 'ttl', [key])

        except Exception as e:
            if USE_LOGGER:
                test_logger.error(err_prefix + "Redis cache failed on command GET key: " + key)
                test_logger.error(str(e))
            else:
                print(err_prefix + "Redis cache failed on command GET key: " + key)
                print(str(e))

            cache_status = REDIS_CACHE_FAILED

        try:
            # cache.do("custom", 'GET', [key])
            # get time to live
            ttl2 = cache.do("custom", 'ttl', [key])

        except Exception as e:
            if USE_LOGGER:
                test_logger.error(err_prefix + "Custom cache failed on command GET key: " + key)
                test_logger.error(str(e))
            else:
                print(err_prefix + "Custom cache failed on command GET key: " + key)
                print(str(e))

            cache_status = REDIS_CACHE_FAILED if SUCCESS else BOTH_CACHES_FAILED

        
        if cache_status==BOTH_CACHES_FAILED:
            test_logger.error(err_prefix + "Custom cache and Redis cache both failed! GET key: " + key)

        print(colored("---ttl1: ", "yellow"), ttl1)
        print(colored("---ttl2: ", "yellow"), ttl2)

        if (ttl1 is not None and ttl1>0) or (ttl2 is not None and ttl2>0):
            return True
        return False


    def get_from_cache(self, url, parameters={}):
        cache_status = SUCCESS

        err_prefix = "ERROR: ResponseCaching: is_in_cache() "

        cache = self.cache

        # key = "response_cached:" + url
        key = "response_cached:" + url + "|" + "p:" + str(parameters) 

        result1 = None
        result2 = None

        try:
            result1 = cache.do("redis", 'get', [key])
        except Exception as e:
            if USE_LOGGER:
                test_logger.error(err_prefix + "Redis cache failed on command GET key: " + key)
                test_logger.error(str(e))
            else:
                print(err_prefix + "Redis cache failed on command GET key: " + key)
                print(str(e))
            cache_status = REDIS_CACHE_FAILED

        try:
            result2 = cache.do("custom", 'get', [key])

        except Exception as e:
            if USE_LOGGER:
                test_logger.error(err_prefix + "Custom cache failed on command GET key: " + key)
                test_logger.error(str(e))
            else:
                print(err_prefix + "Custom cache failed on command GET key: " + key)
                print(str(e))

            cache_status = REDIS_CACHE_FAILED if SUCCESS else BOTH_CACHES_FAILED

        
        if cache_status==BOTH_CACHES_FAILED:
            if USE_LOGGER:
                test_logger.error(err_prefix + "Custom cache and Redis cache both failed! GET key: " + key)
            else:
                print(err_prefix + "Custom cache and Redis cache both failed! GET key: " + key)

        if result1 is not None:
            return result1

        return result2 #! can be None

        
    def remove_from_cache(self, url, parameters={}):
        cache_status = SUCCESS
        err_prefix = "ERROR: ResponseCaching: save_response() "

        cache = self.cache

        # key = "response_cached:" + url
        key = "response_cached:" + url + "|" + "p:" + str(parameters) 

        try:
            cache.do("redis", 'delete', [key])
        except Exception as e:
            if USE_LOGGER:
                test_logger.error(err_prefix + "Redis cache failed on command DELETE key: " + key )
                test_logger.error(str(e))
            cache_status = REDIS_CACHE_FAILED

        try:
            cache.do("custom", 'delete', [key])
        except Exception as e:
            if USE_LOGGER:
                test_logger.error(err_prefix + "Custom cache failed on command DELETE key: " + key )
                test_logger.error(str(e))
            cache_status = REDIS_CACHE_FAILED if SUCCESS else BOTH_CACHES_FAILED

        
        if cache_status==BOTH_CACHES_FAILED:
            if USE_LOGGER:
                test_logger.error(err_prefix + "Custom cache and Redis cache both failed! DELETE key: " + key )

            return "error"

        if cache_status==SUCCESS:
            return "success"

        return "error"

