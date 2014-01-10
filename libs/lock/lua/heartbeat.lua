local lock_key = KEYS[1]

local request_id = ARGV[1]

local actual_request_id = redis.call('HGET', lock_key, 'request_id')

if not actual_request_id then
    redis.call('DEL', lock_key)
    return {-2, 'Lock does not exist'}
end

if actual_request_id == request_id then
    local timeout = redis.call('HGET', lock_key, 'timeout')
    local timeout_type = redis.call('HGET', lock_key, 'timeout_type')

    if timeout == nil then
        return {-9, 'CRITICAL: Timeout inaccessible'}
    end
    if timeout_type == nil then
        return {-9, 'CRITICAL: Timeout type inaccessible'}
    end

    if redis.call(timeout_type, lock_key, timeout) ~= 1 then
        return {-9, 'CRITICAL: could not reset expire for lock key'}
    end

    return {0, 'Success'}

else
    return {-1, 'Incorrect request_id'}
end
