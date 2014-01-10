local last_lock_num_key = KEYS[1]
local lock_key = KEYS[2]

local timeout = ARGV[1]
local timeout_type = ARGV[2]

if redis.call('EXISTS', lock_key) ~= 0 then
    return {-1, 'Lock exists'}
end

local request_id = redis.call('INCR', last_lock_num_key)

redis.call('HMSET', lock_key,
           'request_id', request_id,
           'timeout_type', timeout_type,
           'timeout', timeout)
redis.call(timeout_type, lock_key, timeout)

return {request_id, 'Success'}
