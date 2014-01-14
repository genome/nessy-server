# /v1/resources/
## GET
Returns a list of resources (useful for maintenance).


# /v1/resources/(resource-name)/
## GET
Returns lock data:
- owner request id (url to owner's request)
- owner data
- time until expiration
- queued locks (urls)

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

Body:
{
    "resource_name": (resource_name),
    "timeout": (in seconds),
    "requester_data": (potentially application specific),
    "try_lock": (default false)
}


# /v1/locks/(request-id)/
## GET
Get full request data:
- lock name
- timeout
- requester data
- status (queued, active, expired?, released?)
    - with current prototype backend, expired and released would give 404s

Clients poll this uri until their lock is active.

## PATCH
## PUT
Heartbeat is accomplished by updating the ttl

## DELETE
Release a lock or dequeue a request.
A user can generally only delete their own locks (except for maintenance).
    - How does an application override a lock?
