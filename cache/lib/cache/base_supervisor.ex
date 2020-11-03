defmodule Cache.BaseSupervisor do
    use Supervisor

    def start_link do
        Supervisor.start_link(__MODULE__, [], name: CacheSupervisor)
    end

    def init(_) do
        children = [
            {Cache.Storage.Extra, %{}},
            {Cache.Storage, %{}},
            {Task.Supervisor, name: Cache.MessageListener.Supervisor},
            {Cache.ConnectionListener, []},
            {Cache.LiveManager, []}
        ]

        Supervisor.init(children, strategy: :one_for_one)
    end
end