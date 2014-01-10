local lock_key = KEYS[1]
local timeout_key = KEYS[2]

local secret = ARGV[1]

local actual_secret = redis.call('GET', lock_key)

if not actual_secret then
    redis.call('DEL', timeout_key)
    return {-2, 'Lock does not exist'}
end

if actual_secret == secret then
    redis.call('DEL', lock_key, timeout_key)
    return {0, 'Success'}
else
    return {-1, 'Incorrect secret'}
end
