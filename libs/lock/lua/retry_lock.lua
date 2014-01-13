local lock_key = KEYS[1]
local lock_queue = KEYS[2]
local lock_queue_timeout_types = KEYS[3]
local lock_queue_timeouts = KEYS[4]
local lock_queue_data = KEYS[5]

local request_id = ARGV[1]

local promote_rv = queue_promote(lock_key, lock_queue, lock_queue_timeout_types,
    lock_queue_timeouts, lock_queue_data)
if promote_rv ~= 0 then
    queue_update_timeout(lock_queue,
        lock_queue_timeout_types, lock_queue_timeouts,
        lock_queue_data)
end

local owner_request_id = redis.call('HGET', lock_key, 'request_id')
local owner_data = redis.call('HGET', lock_key, 'data')

if owner_request_id == request_id then
    return {0, 1, request_id, owner_data}

else
    if redis.call('HEXISTS', lock_queue_timeout_types, request_id) == 1 then
        if promote_rv == 0 then
            queue_update_timeout(lock_queue,
                lock_queue_timeout_types, lock_queue_timeouts,
                lock_queue_data)
        end

        return {0, 0, owner_request_id, owner_data}

    else
        return {-1, 0, owner_request_id, owner_data}

    end
end
