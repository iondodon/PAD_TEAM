import grequests
from termcolor import colored

class TwoPhaseCommit():
    # def __init__():
    #   pass
    
    def create_transaction(self):
        # TODO: generate transaction id (unique) + cache
        # add in cache in "active_transactions" this tid
        self.tid = 1
        # return self.tid

    def prepare_transaction(self, service_addresses, parameters={}):
        """ prepare transaction by sending requests to each service from service_addresses list"""

        # TODO: test and log!!!

        hasSuccess = True

        parameters["tid"] = self.tid

        requests_list = []
        for address in service_addresses:
            endpoint = address + "/prepare_transaction"
            r = grequests.get(endpoint, params=parameters)
            requests_list.append(r)

        try:
            rs = grequests.map([r], exception_handler=self.exception_handler)
            for response in rs:
                if response is None or response.json() != "prepared":  #TODO
                    hasSuccess = False

        except Exception as e:
            hasSuccess = False
            # TODO: log using logger
            print("Exception: " + str(e))

        return hasSuccess #returns true or false if all services from list are prepared


    def commit_transaction(self, service_addresses, parameters={}):
        """ commit transaction by sending requests to each service from service_addresses list"""
        hasSuccess = True

        parameters["tid"] = self.tid

        requests_list = []
        for address in service_addresses:
            endpoint = address + "/commit_transaction"
            r = grequests.get(endpoint, params=parameters)
            requests_list.append(r)

        try:
            rs = grequests.map([r], exception_handler=self.exception_handler)
            for response in rs:
                if response is None or response.json() != "success":  #TODO
                    hasSuccess = False

        except Exception as e:
            hasSuccess = False
            # TODO: log using logger
            print("Exception: " + str(e))

        return hasSuccess


    def abort_transaction(self, service_addresses):
        """ abort transaction by sending requests to each service from service_addresses list"""
        parameters = {}
        parameters["tid"] = self.tid

        requests_list = []
        for address in service_addresses:
            endpoint = address + "/abort_transaction"
            r = grequests.get(endpoint, params=parameters)
            requests_list.append(r)

        try:
            rs = grequests.map([r], exception_handler=self.exception_handler)
            for response in rs:
                if response is None or response.json() != "success":  #TODO sau de verificat daca status nu e 200
                    # TODO: in logger
                    return {"status": "error", "message": "abort transaction failed"}

        except Exception as e:
            hasSuccess = False
            # TODO: log using logger
            print("Exception: " + str(e))
            return {"status": "error", "message": "abort transaction failed"}

        return {"status": "success", "message": "abort transaction succeeded"}


    def end_transaction(self):
        # TODO (remove tid from cache???)
        # TODO: remove from cache in "active_transactions" this tid
        pass


    # TODO: oare trebuie sa fie async???? 2PC e sincron de fapt!
    def perform(self, service_addresses, parameters={}):
        self.create_transaction()
        status_prepared = self.prepare_transaction(service_addresses, parameters)
        
        if status_prepared==True:
            self.commit_transaction(service_addresses, parameters)
        else:
            self.abort_transaction(service_addresses)

        self.end_transaction()


    def exception_handler(self, request, exception):
        # TODO: add this in logger
        print(colored("Request failed", "red"))
        print(colored("--request:", "red"), request)
        print(colored("--exception:", "red"), exception)


