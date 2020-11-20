from circuitbreaker  import CircuitBreaker


class LoadBalancer:

	def any_available(self, redis_cache, service_type):
		""" returns True if any service of respective type is available or False if not"""
		return redis_cache.llen("services-" + str(service_type))
		

	def next(self, redis_cache, service_type):
		circuitbreaker = CircuitBreaker(redis_cache.rpoplpush("services-"+str(service_type), "services-"+str(service_type)), service_type)

		return circuitbreaker