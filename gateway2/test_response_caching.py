from response_caching import ResponseCaching
import requests
from termcolor import colored

if __name__ == '__main__':
	response_caching = ResponseCaching()
	
	url = "http://localhost:8001/test-route-t2"
	parameters = {"data": "test"}


	if response_caching.is_in_cache(url, parameters):
		res = response_caching.get_from_cache(url, parameters)
		print(colored("Get from cache:---", "magenta"), res)
	else:
		print(colored("Not in cache, make request:---", "cyan"))

		response = requests.get(url, params=parameters)
		print("-- reponse:", response.content)	
		print(colored("-- reponse code:" + str( response.status_code), "blue"))

		res = response_caching.save_response(url, parameters, response.content)

