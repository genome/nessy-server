local last_request_id = KEYS[1]
local lock_key = KEYS[2]
local lock_queue = KEYS[3]
local lock_queue_timeout_types = KEYS[4]
local lock_queue_timeouts = KEYS[5]
local lock_queue_data = KEYS[6]

local timeout = ARGV[1]
local timeout_type = ARGV[2]
local data = ARGV[3]


local promote_rv = queue_promote(lock_key, lock_queue, lock_queue_timeout_types,
    lock_queue_timeouts, lock_queue_data)

if promote_rv == 0 then
    local request_id = redis.call('INCR', last_request_id)
    redis.call('HMSET', lock_key,
               'request_id', request_id,
               'timeout_type', timeout_type,
               'timeout', timeout,
               'data', data)
    redis.call(timeout_type, lock_key, timeout)

    return {1, request_id, request_id, data}

else
    local owner_id = redis.call('HGET', lock_key, 'request_id')
    local owner_data = redis.call('HGET', lock_key, 'data')

    return {0, -1, owner_id, owner_data}
end
