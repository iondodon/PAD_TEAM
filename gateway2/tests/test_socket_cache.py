import socket
import sys
from time import sleep
import os

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
custom_cache_host = os.environ.get("CUSTOM_CACHE_HOST", 'localhost')
custom_cache_port = os.environ.get("CUSTOM_CACHE_PORT", 6666)

# Connect the socket to the port where the server is listening
server_address = (custom_cache_host, int(custom_cache_port))
print (sys.stderr, 'connecting to %s port %s' % server_address)
sock.connect(server_address)

try:
    # Send data
    message = b'SET test 1\n'
    print(sys.stderr, 'sending "%s"' % message)
    # sock.sendall(message)
    sock.send(message)

    sleep(2)

    # Look for the response
    amount_received = 0
    amount_expected = 1
    
    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
        print(sys.stderr, '-----received "%s"' % data)

    sleep(2)

    # Send data
    message = b'GET test \n'
    print(sys.stderr, 'sending "%s"' % message)
    # sock.sendall(message)
    sock.send(message)

    sleep(2)

    # Look for the response
    amount_received = 0
    amount_expected = 1
    
    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
        print(sys.stderr, '-----received "%s"' % data)

    sleep(2)

    message = b'DEL test 1\n'
    print(sys.stderr, 'sending "%s"' % message)
    # sock.sendall(message)
    sock.send(message)

    sleep(2)

    # Look for the response
    amount_received = 0
    amount_expected = 1
    
    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
        print(sys.stderr, '-----received "%s"' % data)

    sleep(2)

    message = b'GET test\n'
    print(sys.stderr, 'sending "%s"' % message)
    # sock.sendall(message)
    sock.send(message)

    sleep(2)

    # Look for the response
    amount_received = 0
    amount_expected = 1
    
    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
        print(sys.stderr, '-----received "%s"' % data)

    sleep(2)

    sleep(5)


finally:
    print(sys.stderr, 'closing socket')
    sock.close()

