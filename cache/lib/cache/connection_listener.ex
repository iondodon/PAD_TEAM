defmodule Cache.ConnectionListener do
    use Task, restart: :permanent
    require Logger

    @cache_port Application.get_env(:cache_port, :port, 6666) 

    def start_link(_args) do
      Task.start_link(__MODULE__, :run, [])
    end
  
    def run() do
      accept(@cache_port)
    end
    
    def accept(port) do
        {:ok, socket} = :gen_tcp.listen(port, [:binary, packet: :line, active: false, reuseaddr: true])
        Logger.info "Accepting connections on port #{port}"
        loop_acceptor(socket)
    end
  
    defp loop_acceptor(socket) do
        {:ok, client} = :gen_tcp.accept(socket)
        Logger.info("New client connected #{Kernel.inspect client}")
        {:ok, pid} = Task.Supervisor.start_child(
          Cache.MessageListener.Supervisor, 
          fn -> Cache.MessageListener.serve(client) end,
          [restart: :permanent]
        )
        :ok = :gen_tcp.controlling_process(client, pid)

        loop_acceptor(socket)
    end
end