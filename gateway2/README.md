useful links:

- elk stack python : https://medium.com/swlh/python-async-logging-to-an-elk-stack-35498432cb0a
- docker-elk: https://github.com/deviantony/docker-elk


Steps to run elk stack gateway2:
1. $ cd docker-elk/
2. $ docker-compose up
3. Go to localhost:5601 (wait for it to start)
4. login with credentials from logstash/pipeline/logstash.conf
5. Access the logger as in example from Test_elk_logger.ipynb or gatewa2.py
