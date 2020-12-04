FROM elixir:1.9.4

COPY ./ /cache-slave
WORKDIR /cache-slave

#RUN apt update && apt install erlang-wx
RUN mix deps.get
RUN mix local.hex --force

CMD iex -S mix
