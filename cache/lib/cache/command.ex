defmodule Cache.Command do
    require Logger
    alias Cache.Storage
    alias Cache.Storage.Extra

    def parse(line) do
        case String.split(line) do
            ["SET", key, value] -> {:ok, {:set, key, value}}
            ["SETNX", key, value] -> {:ok, {:setnx, key, value}}
            ["GET", key] -> {:ok, {:get, key}}
            ["MGET" | keys] -> {:ok, {:mget, keys}}
            ["DEL", key] -> {:ok, {:del, key}}
            ["DEL" | keys] -> {:ok, {:del, keys}}
            ["INCR", key] -> {:ok, {:incr, key}}
            ["LPUSH", key | values] -> {:ok, {:lpush, key, values}}
            ["LLEN", key] -> {:ok, {:llen, key}}
            ["LREM", key, value] -> {:ok, {:lrem, key, value}}
            ["RPOPLPUSH", key1, key2] -> {:ok, {:rpoplpush, key1, key2}}
            ["EXPIRE", key, sec] -> {:ok, {:expire, key, sec}}
            ["TTL", key] -> {:ok, {:ttl, key}}
            _ -> {:error, :unknown_command}
          end
    end

    # Command execution

    def run(command)

    def run({:set, key, value}) do
        Logger.info("SET #{key} to #{value}")
        Storage.set(key, value)
    end

    def run({:setnx, key, value}) do
        Logger.info("SET  #{key} to #{value}, if not exists")
        Storage.setnx(key, value)
    end

    def run({:get, key}) do
        Logger.info("GET #{key}")
        Storage.get(key)
    end

    def run({:mget, keys}) do
        keys_str = Enum.reduce(keys, "", fn key, keys_str -> keys_str <> key <> " " end)
        Logger.info("MGET #{keys_str}")
        values = Storage.mget(keys)
        IO.inspect(values)
        Enum.reduce(values, "", fn value, str -> str <> value <> " " end)
    end

    @doc """
    Deletes multiple keys
    """
    def run({:del, keys}) when is_list(keys) do
        keys_str = Enum.reduce(keys, "", fn key, keys_str -> keys_str <> key <> " " end)
        Logger.info("DELETE #{keys_str}")
        Storage.delete_keys(keys)
    end

    def run({:del, key}) do
        Logger.info("DELETE #{key}")
        Storage.delete_key(key)
    end

    def run({:incr, key}) do
        Logger.info("INCR #{key}")
        Storage.increment(key)
    end

    def run({:lpush, key, values}) do
        Logger.info("LPUSH into #{key} values #{Kernel.inspect(values)}")
        Storage.lpush(key, values)
    end

    def run({:llen, key}) do
        Logger.info("LLEN #{key}")
        Storage.llen(key)
    end

    def run({:lrem, key, value}) do
        Logger.info("LREM  #{value} in #{key}")
        Storage.lrem(key, value)
    end

    def run({:rpoplpush, key1, key2}) do
        Logger.info("RPOPLPUSH #{key1} #{key2}")
        Storage.rpoplpush(key1, key2)
    end

    def run({:ttl, key}) do
        ttl = Extra.get_ttl("ttl#" <> key)
        if ttl != :nil do
            ttl - System.os_time(:second)
        else
            ttl
        end
    end

    def run({:expire, key, sec}) do
        Logger.info("EXPIRE #{key} in #{sec} seconds")
        {sec, _} = Integer.parse(sec)
        ttl = System.os_time(:second) + sec
        Extra.set_key_ttl("ttl#" <> key, ttl)
    end
end