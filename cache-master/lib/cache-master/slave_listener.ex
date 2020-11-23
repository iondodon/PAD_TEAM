defmodule Cache.SlaveListener do
	use Task, restart: :permanent
	require Logger
	alias Cache.SlaveRegistry

	@port_for_slave Application.get_env(:cache_master, :port_for_slave, 6667)
	@recv_length 0

	def start_link(_args) do
		Task.start_link(__MODULE__, :run, [])
	end

	def run() do
		listen(@port_for_slave)
	end

	def listen(port) do
		opts = [:binary, packet: :line, active: false, reuseaddr: true]
		{:ok, socket} = :gen_tcp.listen(port, opts)
		Logger.info "Listening slaves on port #{port}"
		loop_acceptor(socket)
	end

	defp loop_acceptor(socket) do
		{:ok, slave} = :gen_tcp.accept(socket)
		Logger.info("New slave connected #{Kernel.inspect slave}")

		Task.async(fn -> register_slave(slave) end)

		loop_acceptor(socket)
	end

	defp register_slave(slave) do
		{:ok, slave_name} = :gen_tcp.recv(slave, @recv_length)
		slave_name = String.replace(slave_name, "\n", "")
		SlaveRegistry.add_slave(slave_name, slave)
		Logger.info("Slave #{Kernel.inspect(slave)} added")
		IO.inspect(SlaveRegistry.get_registry())
	end
end
