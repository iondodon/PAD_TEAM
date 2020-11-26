from circuitbreaker  import CircuitBreaker
from cache_driver import CacheDriver

class LoadBalancer:

	def any_available(self, service_type):
		""" returns True if any service of respective type is available or False if not"""

		# redis_cache = CacheDriver('redis')
		redis_cache = CacheDriver('custom')

		# return redis_cache.llen("services-" + str(service_type))
		return redis_cache.do('llen', ["services-" + str(service_type)])
		

	def next(self, service_type):
		# circuitbreaker = CircuitBreaker(redis_cache.rpoplpush("services-"+str(service_type), "services-"+str(service_type)), service_type)
		# service = redis_cache.rpoplpush("services-"+str(service_type), "services-"+str(service_type))
		
		# redis_cache = CacheDriver('redis')
		redis_cache = CacheDriver('custom')

		service = redis_cache.do('rpoplpush', ["services-"+str(service_type), "services-"+str(service_type)])
		circuitbreaker = CircuitBreaker(service, service_type)

		return circuitbreaker