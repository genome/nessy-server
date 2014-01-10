local last_lock_num_key = KEYS[1]
local lock_key = KEYS[2]

local timeout = ARGV[1]
local timeout_type = ARGV[2]
local data = ARGV[3]

local request_id = redis.call('INCR', last_lock_num_key)

if redis.call('EXISTS', lock_key) ~= 0 then
    local owner_id = redis.call('HGET', lock_key, 'request_id')
    local owner_data = redis.call('HGET', lock_key, 'data')
    return {0, request_id, owner_id, owner_data}
end

redis.call('HMSET', lock_key,
           'request_id', request_id,
           'timeout_type', timeout_type,
           'timeout', timeout,
           'data', data)
redis.call(timeout_type, lock_key, timeout)

return {1, request_id, request_id, data}
