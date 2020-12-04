FROM elixir:1.9.4

COPY ./ /cache-master
WORKDIR /cache-master

#RUN apt update && apt install erlang-wx
RUN mix local.hex --force

#CMD iex -S mix

EXPOSE 6666 6667