import redis
import os
import socket
import sys
from time import sleep
from termcolor import colored

class CacheDriver(object):
    """Driver for the cache using singleton design pattern slightly modified:
        It allows only one instance of each cache type, for example 1 redis instance, 1 custom instance
    """

    class __OneCacheDriver:
        def __init__(self, cache_type='redis'):
            self.cache_type = cache_type

            if cache_type=='custom':
                self.init_custom_cache()
            else:
                self.init_redis_cache()

        def init_custom_cache(self):
            # Create a TCP/IP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            custom_cache_host = os.environ.get("CUSTOM_CACHE_HOST", 'localhost')
            custom_cache_port = int(os.environ.get("CUSTOM_CACHE_PORT", 6666))

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

                new_args = args
                
                print(colored("Command:", 'red'), command)
                print(colored("Command type:", 'green'), type(command))

                if message_command=='LRANGE':
                    message_command = 'GET'
                    new_args = args[:-2]

                if message_command=='DELETE':
                    message_command = 'DEL'

                for arg in new_args:
                    message_command += " " + str(arg)
                message_command += "\n"


                message = bytes(message_command, 'utf-8')
                # message = bytes(message_command, 'ascii')
                # message = message_command
                print(sys.stderr, 'sending "%s"' % message)

                custom_cache_host = os.environ.get("CUSTOM_CACHE_HOST", 'localhost')
                custom_cache_port = int(os.environ.get("CUSTOM_CACHE_PORT", 6666))
                
                # self.sock.send(message)
                self.sock.sendto(message_command.encode(),(custom_cache_host, custom_cache_port))


                sleep(1)

                data = None
                # Look for the response
                amount_received = 0
                amount_expected = 2
                
                while amount_received < amount_expected and (data==None or data.decode('utf-8')!=''):
                    data = self.sock.recv(1024)
                    amount_received += len(data)
                    print(sys.stderr, 'received "%s"' % data)
                    print("---", data.decode('utf-8'))

                # TODO: test
                data = data.decode('utf-8')
                data = data.replace(' \r\n \r', '')
                data_type = data[data.find("(")+1:data.find(")")]

                print(colored("data:", 'blue'), data)

                # data_separated = data[len(data_type)+2:].replace(" ", '').replace('\n', '')
                data_separated = data[len(data_type)+2:].replace('\n', '').strip()
                print(colored("data_separated:", 'red'), data_separated)

                if data_type == 'integer':
                    return int(data_separated)

                elif data_type=='list':
                    res = []
                    res_item = ""
                    print(colored("data_type:", 'blue'), data_type)

                    for item in data_separated:
                        if item == " ":
                            print(colored("res item:", 'yellow'))
                            res.append(res_item)
                            res_item = ""
                        else:
                            res_item += item

                    # append last item
                    res.append(res_item)

                    
                    print(colored("type data_res:", 'green'), type(res))
                    print(colored("data_res:", 'green'), res)

                    return [res]

                elif data_type == 'binary':

                    return data_separated.replace('"', "").replace("'", '')

                elif data_type=='atom':
                    return None

                # return data.decode('utf-8')
                return data_separated

            elif self.cache_type=='redis':
                return getattr(self.cache, command)(*args)

        def get_type(self):
            return self.cache_type

        def __del__(self):
            print(sys.stderr, 'closing socket')
            self.sock.close()


        def __str__(self):
            return repr(self) + " : " + self.cache_type

    instance = {}
    # cache_type = 'redis'

    # def __init__(self, cache_type):
    def __init__(self):
        for cache_type in ["redis", "custom"]:
            if not cache_type in CacheDriver.instance:
                CacheDriver.instance[cache_type] = CacheDriver.__OneCacheDriver(cache_type)
            # self.cache_type = cache_type
        # else:
            # CacheDriver.instance[cache_type].cache_type = cache_type

    def do(self, cache_type, command, args):
        return CacheDriver.instance[cache_type].do(command, args)

    # def get_type(self):
    #     return CacheDriver.instance[cache_type].get_type()
    

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