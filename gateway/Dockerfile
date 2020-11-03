FROM elixir:1.9.4

COPY ./ /gateway
WORKDIR /gateway

RUN rm -rd _build
RUN mix local.hex --force
RUN mix deps.get
RUN mix local.rebar --force

CMD iex -S mix

EXPOSE 4000