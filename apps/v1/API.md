# Locking API Description

## /v1/locks/
### GET
Returns a list of locks.

Response codes:
- 200 (OK) on success


## /v1/locks/(resource-name)/
### GET
Sample response data:

    {
        "owner": "https://api.lock.gsc.wustl.edu/v1/locks/foo-resource-7/requests/27/",
        "requests": [
            "https://api.lock.gsc.wustl.edu/v1/locks/foo-resource-7/requests/27/",
            "https://api.lock.gsc.wustl.edu/v1/locks/foo-resource-7/requests/32/",
            "https://api.lock.gsc.wustl.edu/v1/locks/foo-resource-7/requests/76/",
        ]
    }

Response codes:
- 200 (OK) on success
- 404 (Not Found) if resource doesn't exist


## /v1/locks/(resource-name)/owner/
### GET
Sample response data:

    {
        "duration_active": 4567,
        "time_since_last_heartbeat": 139,
        "ttl": 421,
        "request": "https://api.lock.gsc.wustl.edu/v1/locks/foo-resource-7/requests/27/",
    }

Response codes:
- 200 (OK) on success
- 404 (Not Found) if request doesn't exist


## /v1/locks/(resource-name)/requests/
### POST
Creates a request for the lock.

Sample request data:

    {
        "requester_data": { "foo": "bar" },
        "timeout": 600,
    }

Response codes:
- 201 (Created) if no contention and immediate success
    - header "Location: /v1/locks/(resource-name)/requests/(request-id)/"
- 202 (Accepted) if contention (Location header)
    - header "Location: /v1/locks/(resource-name)/requests/(request-id)/"


### GET
Returns a list of requests associated with the resource.

Response codes:
- 200 (OK) on success
- 404 (Not Found) if resource doesn't exist?


## /v1/locks/(resource-name)/requests/(request-id)/
### GET
Sample response data:

    {
        "creation_time": "2014-01-15 12:41:00 PM",
        "current_status": "active",
        "duration_active": 4567,
        "duration_waiting": 123,
        "requester_data": { "foo": "bar" },
        "resource": "foo-resource-7",
        "statuses": [
            {"timestamp": "2014-01-15 12:41:00 PM", "type": "waiting"},
            {"timestamp": "2014-01-15 12:42:03 PM", "type": "active"},
        ],
        "timeout": 600,
        "url": "https://api.lock.gsc.wustl.edu/v1/locks/foo-resource-7/requests/27/",
    }

Response codes:
- 200 (OK) on success
- 404 (Not Found) if request doesn't exist

### PATCH/PUT
Update lock ttl (don't allow arbitrary attribute updates?).

Response codes:
- 204 (No Content) on success
- 404 (Not Found) if request doesn't exist
- 412 (Precondition Failed) if request is not active

### DELETE
Update request status to 'released' or 'abandoned' from 'active' or 'waiting'
respectively.

Response codes:
- 204 (No Content) on success
- 404 (Not Found) if request doesn't exist
- 412 (Precondition Failed) if request is already released or abandoned
