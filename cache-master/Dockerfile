FROM elixir:1.9.4

COPY ./ /
WORKDIR /

#RUN apt update && apt install erlang-wx
RUN rm -rf _build/

RUN mix local.hex --force && mix deps.get

CMD iex -S mix

EXPOSE 6666 6667
