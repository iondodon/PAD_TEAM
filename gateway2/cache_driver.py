import redis


class CacheDriver(object):
    """Driver for the cache using singleton design pattern"""

    class __OneCacheDriver:
        def __init__(self, cache_type='redis'):
            if cache_type=='custom':
                self.cache_type = cache_type
                self.init_custom_cache()
            else:
                self.cache_type = 'redis'
                self.init_redis_cache()

        def init_custom_cache(self):
            # TODO
            pass

        def init_redis_cache(self):
            """Setup Redis cache"""
            # from local:
            self.cache = redis.Redis(host='localhost', port=6379, db=0)
            # from docker-compose:
            # self.cache = redis.Redis(host='redis', port=6380, db=0)



        def do(self, command, args):
            """ Perform a command to the cache with the required arguments in the form of a list"""
            if self.cache_type=='custom':
                # TODO
                pass

            elif self.cache_type=='redis':
                return getattr(self.cache, command)(*args)


        def __str__(self):
            return repr(self) + " : " + self.cache_type

    instance = None

    def __init__(self, cache_type):
        if not CacheDriver.instance:
            CacheDriver.instance = CacheDriver.__OneCacheDriver(cache_type)
        else:
            CacheDriver.instance.cache_type = cache_type

    def do(self, command, args):
        return CacheDriver.instance.do(command, args)


# https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
# Example of singleton class design pattern:
# class OnlyOne:
#     class __OnlyOne:
#         def __init__(self, arg):
#             self.val = arg
#         def __str__(self):
#             return repr(self) + self.val

#     instance = None

#     def __init__(self, arg):
#         if not OnlyOne.instance:
#             OnlyOne.instance = OnlyOne.__OnlyOne(arg)
#         else:
#             OnlyOne.instance.val = arg

#     def __getattr__(self, name):
#         return getattr(self.instance, name)