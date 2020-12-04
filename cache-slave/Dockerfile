FROM elixir:1.9.4

COPY ./ /cache-slave
WORKDIR /cache-slave

#RUN apt update && apt install erlang-wx
RUN rm -rf _build

RUN mix local.hex --force && mix deps.get

CMD iex -S mix

# CMD iex -S mix
