local lock_key = KEYS[1]

local request_id = ARGV[1]

local actual_request_id = redis.call('HGET', lock_key, 'request_id')

if not actual_request_id then
    redis.call('DEL', lock_key)
    return {-2, 'Lock does not exist'}
end

if actual_request_id == request_id then
    redis.call('DEL', lock_key)
    return {0, 'Success'}
else
    return {-1, 'Incorrect request_id'}
end
