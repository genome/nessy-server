local lock_key = KEYS[1]
local timeout_key = KEYS[2]

local request_id = ARGV[1]

local actual_request_id = redis.call('GET', lock_key)

if not actual_request_id then
    redis.call('DEL', timeout_key)
    return {-2, 'Lock does not exist'}
end

if actual_request_id == request_id then
    local timeout = redis.call('GET', timeout_key)

    if not timeout then
        return {-9, 'CRITICAL: Timeout inaccessible'}
    end

    local pre_ttl = redis.call('TTL', lock_key)

    if redis.call('EXPIRE', lock_key, timeout) ~= 1 then
        return {-9, 'CRITICAL: could not reset expire for lock key'}
    end
    if redis.call('EXPIRE', timeout_key, timeout) ~= 1 then
        return {-9, 'CRITICAL: could not reset expire for lock timeout key'}
    end

    return {0, 'Success'}

else
    return {-1, 'Incorrect request_id'}
end
