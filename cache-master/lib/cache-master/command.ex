defmodule Cache.Command do
    require Logger
    alias Cache.SlaveRegistry

    @recv_length 0
    @tag_replicas "replicas#"

    # Command execution on slave
    def run(command) do
        registry = SlaveRegistry.get_registry()

        [first_slave_name | _tail] = Map.get(registry, "slaves", [])
        [first_replica_socket | _tail] = Map.get(registry, @tag_replicas <> first_slave_name)


        Logger.info("EXECUTE #{command} on slave #{Kernel.inspect(first_replica_socket)}")
        :gen_tcp.send(first_replica_socket, command)

        {:ok, response_from_slave} = :gen_tcp.recv(first_replica_socket, @recv_length)
        Logger.info(response_from_slave)
        response_from_slave
    end
end
