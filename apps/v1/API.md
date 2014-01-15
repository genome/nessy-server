# /v1/locks/
## GET
Returns a list of locks (useful for maintenance).

# /v1/locks/(resource-name)/owner/
## GET


# /v1/locks/(resource-name)/requests/
## POST
Creates a request for the lock.
Sets Location header to /v1/locks/(resource-name)/requests/(request-id)/

Sample body:

    {
        "requester_data": { "foo": "bar" },
        "timeout": 600,
    }

Returns:
- 201 (Created) if no contention and immediate success (Location header)
- 202 (Accepted) if contention and `try_lock` not set (Location header)
- 409 (Conflict) if contention and `try_lock` is set


## GET
Returns a list of requests associated with the resource.

# /v1/locks/(resource-name)/requests/(request-id)/
## GET

## PATCH/PUT

## DELETE





<!-- old -->


# /v1/locks/(resource-name)/
## GET
Sample data:

    {
        "url": "https://api.lock.gsc.wustl.edu/v1/resources/asdf/",
        "owner": {
            "url": "https://api.lock.gsc.wustl.edu/v1/locks/45/",
            "active_time": 1234
        },
        "queue": [
            "url": "https://api.lock.gsc.wustl.edu/v1/locks/92/",
            "url": "https://api.lock.gsc.wustl.edu/v1/locks/97/",
        ]
    }

## DELETE
Deletes the resource and all locks.
This is a maintenance task, do not allow for general users.
Omit for now?

Returns:
- 204 (No Content) on success
- 404 (Not Found) if no locks exist for the resource


# /v1/locks/
## POST
Creates a request for the lock.
Sets Location header to the new lock [/v1/locks/(request-id)/].

Sample body:

    {
        "niceness": 10,
        "requester_data": { "foo": "bar" },
        "resource": "https://api.lock.gsc.wustl.edu/v1/resources/asdf/",
        "timeout": 600,
        "try_lock": false,
    }

Returns:
- 201 (Created) if no contention and immediate success (Location header)
- 202 (Accepted) if contention and `try_lock` not set (Location header)
- 409 (Conflict) if contention and `try_lock` is set


# /v1/locks/(request-id)/
## GET
Clients poll this uri until their lock is active.

Sample data:

    {
        "active_time": 4567,
        "niceness": 10,
        "requester_data": { "foo": "bar" },
        "resource": "https://api.lock.gsc.wustl.edu/v1/resources/asdf/",
        "status": "active",
        "timeout": 600,
        "try_lock": false,
        "ttl": 421,
        "url": "https://api.lock.gsc.wustl.edu/v1/locks/32/",
        "wait_time": 123,
    }

Returns:
- 200 (OK) on success
- 404 (Not Found) if lock doesn't exist

## PATCH
## PUT
Heartbeat is accomplished by updating the ttl

Returns:
- 204 (No Content) on success
- 404 (Not Found) if lock doesn't exist

## DELETE
Release a lock or dequeue a request.
A user can generally only delete their own locks (except for maintenance).
    - How does an application override a lock?

Returns:
- 204 (No Content) on success
- 404 (Not Found) if lock doesn't exist
