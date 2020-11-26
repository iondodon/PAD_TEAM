import redis
import os
import socket
import sys
from time import sleep

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
            # Create a TCP/IP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            custom_cache_host = os.environ.get("CUSTOM_CACHE_HOST", 'localhost')
            custom_cache_port = os.environ.get("CUSTOM_CACHE_PORT", 6666)

            # Connect the socket to the port where the server is listening
            server_address = (custom_cache_host, int(custom_cache_port))
            print (sys.stderr, 'connecting to %s port %s' % server_address)
            self.sock.connect(server_address)


        def init_redis_cache(self):
            """Setup Redis cache"""
            # from local:
            redis_host = os.environ.get("REDIS_HOST", 'localhost')
            redis_port = os.environ.get("REDIS_PORT", 6379)

            # self.cache = redis.Redis(host='localhost', port=6379, db=0)
            # from docker-compose:
            # self.cache = redis.Redis(host='redis', port=6380, db=0)

            self.cache = redis.Redis(host=redis_host, port=redis_port, db=0)



        def do(self, command, args):
            """ Perform a command to the cache with the required arguments in the form of a list"""
            if self.cache_type=='custom':
                 # Send data
                message_command = command.upper()
                for arg in args:
                    message_command += " " + str(arg)
                message_command += "\n"

                message = bytes(message_command, 'utf-8')
                # message = bytes(message_command, 'ascii')
                # message = message_command
                print(sys.stderr, 'sending "%s"' % message)

                self.sock.send(message)

                sleep(1)

                # Look for the response
                amount_received = 0
                amount_expected = 1
                
                while amount_received < amount_expected:
                    data = self.sock.recv(16)
                    amount_received += len(data)
                    print(sys.stderr, 'received "%s"' % data)
                    print("---", data.decode('utf-8'))

                # TODO: test
                data = data.decode('utf-8')
                data = data.replace(' \r\n \r', '')
                data_type = data[data.find("(")+1:data.find(")")]
                if data_type == 'integer':
                    return int(data[len(data_type)+1:].replace(" ", ''))

                # return data.decode('utf-8')
                return data

            elif self.cache_type=='redis':
                return getattr(self.cache, command)(*args)

        def __del__(self):
            print(sys.stderr, 'closing socket')
            self.sock.close()


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