from circuitbreaker  import CircuitBreaker
from cache_driver import CacheDriver

import logging
from logstash_async.handler import AsynchronousLogstashHandler
from time import sleep
from sanic import response


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


###### Define possible cache statuses#####
SUCCESS = 1
CUSTOM_CACHE_FAILED = 2
REDIS_CACHE_FAILED = 3
BOTH_CACHES_FAILED = 4
##########################################


class LoadBalancer:

    def any_available(self, service_type):
        """ returns True if any service of respective type is available or False if not"""
        cache_status = SUCCESS

        len_services1 = 0
        len_services2 = 0

        cache = CacheDriver()
        try:
            len_services1 = cache.do("custom", 'llen', ["services-" + str(service_type)])
        except Exception as e:
            test_logger.error("ERROR: Custom cache llen command failed on key" + "services-" + str(service_type)  )
            test_logger.error(str(e))
            cache_status = CUSTOM_CACHE_FAILED
        
        try:        
            len_services2 = cache.do("redis", 'llen', ["services-" + str(service_type)])
        except Exception as e:
            test_logger.error("ERROR: Redis cache llen command failed on key" +"services-" + str(service_type)  )
            test_logger.error(str(e))
            cache_status = REDIS_CACHE_FAILED if SUCCESS else BOTH_CACHES_FAILED

        
        if cache_status == BOTH_CACHES_FAILED:
            test_logger.error("ERROR: Alert! Both caches failed (redis and custom) on command llen (" + "services-" + str(service_type) + ")")


        if len_services1 is None or type(len_services1) is not int:
            len_services1 = 0
        
        if len_services2 is None or type(len_services2) is not int:
            len_services2 = 0

        # return len_services
        return max(int(len_services1), int(len_services2))>0 #will return true or false

        

    def next(self, service_type):
        # circuitbreaker = CircuitBreaker(redis_cache.rpoplpush("services-"+str(service_type), "services-"+str(service_type)), service_type)
        # service = redis_cache.rpoplpush("services-"+str(service_type), "services-"+str(service_type))
        cache_status = SUCCESS


        sleep(0.3)  #give some time for processing previous request
        cache = CacheDriver()

        service1 = None
        service2 = None

        try:
            service1 = cache.do("custom", 'rpoplpush', ["services-"+str(service_type), "services-"+str(service_type)])
        except Exception as e:
            test_logger.error("ERROR: Custom cache rpoplpush command failed on" + str(["services-"+str(service_type), "services-"+str(service_type)]))
            test_logger.error(str(e))
            cache_status = CUSTOM_CACHE_FAILED

        try:
            service2 = cache.do("redis", 'rpoplpush', ["services-"+str(service_type), "services-"+str(service_type)])
            if service2 is not None:
                service2 = service2.decode('utf-8')

        except Exception as e:
            test_logger.error("ERROR: Redis cache rpoplpush command failed on" + str(["services-"+str(service_type), "services-"+str(service_type)]))
            test_logger.error(str(e))
            cache_status = REDIS_CACHE_FAILED if SUCCESS else BOTH_CACHES_FAILED
            
        

        if cache_status == BOTH_CACHES_FAILED:
            test_logger.error("ERROR: Alert! Both caches rpoplpush command failed on " + str(["services-"+str(service_type), "services-"+str(service_type)]))

        if service1 is not None:
            circuitbreaker = CircuitBreaker(service1, service_type)
        elif service2 is not None:
            circuitbreaker = CircuitBreaker(service2, service_type)

        return circuitbreaker