FROM openjdk:11.0.8-buster

WORKDIR /app
COPY . /app/

RUN apt update
RUN apt install maven -y

RUN mvn clean install -DskipTests

CMD java -jar -Dserver.port=8080 target/*.jar

EXPOSE 8080