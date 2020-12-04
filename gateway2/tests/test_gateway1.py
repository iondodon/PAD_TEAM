
import requests
import json
from termcolor import colored
import pprint


# SERVER_ADDRESS = 'http://127.0.0.1:5000'
SERVER_ADDRESS = 'http://127.0.0.1:5003'
# SERVER_ADDRESS = 'http://127.0.0.1:5005'
pp = pprint.PrettyPrinter(indent=4)

def make_request(method, endpoint, parameters):
    if method=='GET':
        r = requests.get(endpoint, params=parameters)
    elif method=='POST':
        r = requests.post(endpoint, data=parameters)
    elif method=='PUT':
        r = requests.put(endpoint, data=parameters)
    elif method=='DELETE':
        r = requests.delete(endpoint)


def register_service(service_name, address, service_type):
    endpoint = SERVER_ADDRESS + "/service-register"
    parameters = {
        "service_name": service_name,
        "address": address,
        "type": service_type
    }
    print(colored("-------REQUEST " + endpoint, "blue"))
    print("parameters:", parameters)

    try:
        # r = requests.post(endpoint, data=parameters)
        r = requests.post(endpoint, json=parameters)
        print(colored("response:---", "green"))
        pp.pprint(r.json())

    except Exception as e:
        print(colored("---error in request", "red"), e)
        
        if r is not None:
            print(colored("status code:"+str(r.status_code), "red"))
            print(colored(str(r.text), "red"))
        # print(colored("status code:"+str(r.status_code), "red"))
        # print(colored(str(r), "red"))
        # print(colored(str(r.text), "red"))

    

def request_init_student_dash(student_name, group):
    # curl -d '{"student":"Diana Marusic", "grupa": "FAF-171"}' -H 'Content-Type: application/json' http://127.0.0.1:5000/init_student
    # endpoint = SERVER_ADDRESS + "/init-student"
    endpoint = SERVER_ADDRESS + "/init_student"
    parameters = {
        "student_name": student_name,
        "grupa": group
    }
    print(colored("-------REQUEST " + endpoint, "blue"))
    print("parameters:", parameters)

    try:
        r = requests.post(endpoint, json=parameters)
        print(colored("response:---", "green"))
        pp.pprint(r.json())

    except Exception as e:
        print(colored("---error in request", "red"), e)
        print(colored("status code:"+str(r.status_code), "red"))
        if r is not None:
            print(colored("status code:"+str(r.status_code), "red"))
            print(colored(str(r.text), "red"))



def request_hello_t1(method='GET'):
    # curl -d '{"student":"Diana Marusic", "grupa": "FAF-171"}' -H 'Content-Type: application/json' http://127.0.0.1:5000/init_student
    # endpoint = SERVER_ADDRESS + "/init-student"
    endpoint = SERVER_ADDRESS + "/test-route"
    parameters = {
        "message": "hello",
    }
    print(colored("-------REQUEST " + endpoint, "blue"))
    print("parameters:", parameters)

    try:
        if method=="POST":
            r = requests.post(endpoint, json=parameters)
        else:
            r = requests.get(endpoint, json=parameters)

        print(colored("response:---", "green"))
        pp.pprint(r.json())


    except Exception as e:
        print(colored("---error in request", "red"), e)
        print(colored("status code:"+str(r.status_code), "red"))
        if r is not None:
            print(colored("status code:"+str(r.status_code), "red"))
            print(colored(str(r.text), "red"))



def get_registered_services():
    # curl  http://127.0.0.1:5000/registered-services

    endpoint = SERVER_ADDRESS + "/registered-services"
    print(colored("-------REQUEST " + endpoint, "blue"))

    r = None
    try:
        r = requests.get(endpoint)
        print(colored("response:---", "green"))
        pp.pprint(r.json())
    except Exception as e:
        print(colored("---error in request", "red"), e)
        if r is not None:
            print(colored("status code:"+str(r.status_code), "red"))
            print(colored(str(r.text), "red"))
        


# do not forget to change parameter to 'RPC' in circuitbreaker!
def test_gateway_rpc():
    register_service(service_name="ServiceRPC1_new", address="http://127.0.0.1:6003/", service_type="type1")
    get_registered_services()
    request_init_student_dash("Diana 1", "FAF-171")


# do not forget to change parameter to 'HTTP' in circuitbreaker!
def test_gateway_http():
    # register_service("Service1", "http://127.0.0.1:6002/", "type1")
    # register_service("Service2", "http://127.0.0.1:6001/", "type2")
    # register_service("Service1", "http://127.0.0.1:6004/", "type1")

    # register_service(service_name="Service2", address="http://127.0.0.1:6004/", service_type="type1")
    
    # register_service(service_name="Service1", address="http://127.0.0.1:6005/", service_type="type1")

    get_registered_services()
    request_hello_t1(method='GET')
    # request_hello_t1(method='POST')
    # request_init_student_dash("Diana 2", "FAF-171")

if __name__ == '__main__':
    # HTTP:
    test_gateway_http()

    # RPC:
    # test_gateway_rpc()