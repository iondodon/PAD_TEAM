FROM elixir:1.9.4

COPY ./ /cache
WORKDIR /cache
EXPOSE 6666

RUN rm -rd _build
RUN mix local.hex --force
RUN mix deps.get
RUN mix local.rebar --force

CMD iex -S mix