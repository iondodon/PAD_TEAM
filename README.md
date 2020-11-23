# PAD_TEAM

"SET key value" -> "(atom) ok"
"SETNX key value" -> "(atom) ok"
"GET key" -> "(integer) value"
"MGET key1 key2 [...]" -> not working
"DEL key" -> "(integer) value"
"DEL key1 key2 [...]" -> not working
"INCR key" -> "(binary) 'value'"
"LPUSH key val1 val2 [...]" -> "(integer) length" 
"LLEN key" -> "(integer) value"
"LREM key value" -> "(integer) count"
"RPOPLPUSH key1 key2" -> "(integer) val"
"EXPIRE key sec" -> ...
"TTL key" -> ...
