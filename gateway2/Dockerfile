from python:3.8
WORKDIR /
ENV LANG=en_US.UTF-8

EXPOSE 5003

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

# Now it is started from docker-compose, this is why it is commented
# CMD ["python", "-u", "app.py"]