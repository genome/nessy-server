# /v1/resources/
## GET
Returns a list of resources (useful for maintenance).


# /v1/resources/(resource-name)/
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


# /v1/locks/
## GET
Returns a list of locks.
Omit for now?

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

## PATCH
## PUT
Heartbeat is accomplished by updating the ttl

## DELETE
Release a lock or dequeue a request.
A user can generally only delete their own locks (except for maintenance).
    - How does an application override a lock?
