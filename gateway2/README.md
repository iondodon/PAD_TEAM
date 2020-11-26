useful links:

- elk stack python : https://medium.com/swlh/python-async-logging-to-an-elk-stack-35498432cb0a
- docker-elk: https://github.com/deviantony/docker-elk

### Steps to run docker with gateway2 and elk stack:
1. ``` $ docker build -t flask-gateway . ```
2. ``` $ docker-compose up ```
3. Go to localhost:5601 (wait for it to start)
4. login with credentials from docker-elk/logstash/pipeline/logstash.conf


### Logging
if you don't want to see debug level logs in elk, then change variable "FLASK_ENV" not to be development and
in gateway.py set app.config["DEBUG"] to False


### Steps to run elk stack gateway2:
1. $ cd
2. $ docker-compose up
3. Go to localhost:5601 (wait for it to start)
4. login with credentials from docker-elk/logstash/pipeline/logstash.conf
5. Access the logger as in example from Test_elk_logger.ipynb or gateway2.py



### Old instructions - Steps to run elk stack gateway2:
1. $ cd docker-elk/
2. $ docker-compose up
3. Go to localhost:5601 (wait for it to start)
4. login with credentials from logstash/pipeline/logstash.conf
5. Access the logger as in example from Test_elk_logger.ipynb or gatewa2.py


### Warnings and Problem solving
- if problem with apturl, this is a specific package to Ubuntu, so in docker it works without, on Ubuntu without docker it might not work

- to stop redis server locally on Ubuntu:
```$ /etc/init.d/redis-server stop ```
- to start redis server locally on Ubuntu:
```$ /etc/init.d/redis-server start ```

### Running in docker-compose gateway with elk stack:
- in code in flask set logger host to be name of the service, in this case logstash
- add same network elk (maybe doesn't help as much as the previous point)

### Useful resources for logging:
- https://docs.python.org/3/howto/logging.html
- https://www.scalyr.com/blog/the-10-commandments-of-logging/