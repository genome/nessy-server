local lock_key = KEYS[1]
local timeout_key = KEYS[2]

local secret = ARGV[1]

local actual_secret = redis.call('GET', lock_key)

if not actual_secret then
    redis.call('DEL', timeout_key)
    return {-2, 'Lock does not exist'}
end

if actual_secret == secret then
    local timeout = redis.call('GET', lock_key)
    if not timeout then
        return {-3, 'CRITICAL: Timeout inaccessible'}
    end

    redis.call('EXPIRE', lock_key, timeout)
    redis.call('EXPIRE', timeout_key, timeout)
    return {0, 'Success'}

else
    return {-1, 'Incorrect secret'}
end
