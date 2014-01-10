local last_lock_num_key = KEYS[1]
local lock_key = KEYS[2]
local timeout_key = KEYS[3]

local timeout = ARGV[1]

if redis.call('EXISTS', lock_key) ~= 0 then
    return {-1, 'Lock exists'}
end

local secret = redis.call('INCR', last_lock_num_key)
redis.call('SET', lock_key, secret, 'EX', timeout)
redis.call('SET', timeout_key, timeout, 'EX', timeout)

return {secret, 'Success'}
