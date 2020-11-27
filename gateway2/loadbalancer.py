from circuitbreaker  import CircuitBreaker
from cache_driver import CacheDriver

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


class LoadBalancer:

    def any_available(self, service_type):
        """ returns True if any service of respective type is available or False if not"""

        try:
            redis_cache = CacheDriver('redis')
        except:
            test_logger.error("ERROR: Redis cache initialization failed")
        try:
            cache = CacheDriver('custom')
        except:
            test_logger.error("ERROR: Custom cache initialization failed")
        

        try:
            len_services = cache.do('llen', ["services-" + str(service_type)])
        except:
            test_logger.error("ERROR: Custom cache llen command failed")

            len_services = redis_cache.do('llen', ["services-" + str(service_type)])

        return len_services

        

    def next(self, service_type):
        # circuitbreaker = CircuitBreaker(redis_cache.rpoplpush("services-"+str(service_type), "services-"+str(service_type)), service_type)
        # service = redis_cache.rpoplpush("services-"+str(service_type), "services-"+str(service_type))
        
        try:
            redis_cache = CacheDriver('redis')
        except:
            test_logger.error("ERROR: Redis cache initialization failed")
        try:
            cache = CacheDriver('custom')
        except:
            test_logger.error("ERROR: Custom cache initialization failed")
        
        try:
            service = cache.do('rpoplpush', ["services-"+str(service_type), "services-"+str(service_type)])
            test_logger.error("ERROR: Custom cache rpoplpush command failed")
        except:
            service = redis_cache.do('rpoplpush', ["services-"+str(service_type), "services-"+str(service_type)]).decode('utf-8')

        circuitbreaker = CircuitBreaker(service, service_type)

        return circuitbreaker