# Locking System Requirements
## Contention
- A queue of waiting claims should be kept for each resource.
- When a claim loses its 'active' status, the next claim in the queue for that
  resource should be changed from 'waiting' to 'active'.
- Claim status should be updated by the server from 'active' to 'expired' after
  that claim's ttl is less than 0.


## Performance
Should support N requests per second.

- "realistic" distribution of request types should be considered
    - ~100/s PATCH requests for status from 'waiting' to 'active'


## Authentication & Authorization
Should require minimal effort to integrate with standard auth systems like
OAuth and Shibboleth.


## Miscellaneous Details
- times should be in seconds as floats (timeout, ttl, durations)
- 'revoked' status is optional (may use 'expired' instead)

## POST /v1/claims/
### Parameters
resource

- string
- length > 0
- mandatory

timeout

- float
- seconds
- value >= 0
- mandatory

metadata

- JSON-compatible blob
- optional

### Successful Results
All successful posts should:

- set Location header
- save user-provided data
    - metadata
    - resource
    - timeout
- set automatic fields
    - creation time
    - status

Successful posts without contention should:

- return HTTP 201 (OK)
- set status to 'active'
- set ttl to timeout

Successful posts with contention should:

- return HTTP 202 (Accepted)
- set status to 'waiting'

### Errors
- HTTP 400 (Bad Request)
    - Missing mandatory parameters
    - Invalid values for parameters
    - Unknown parameters


## PATCH or PUT /v1/claims/(id)/
### Parameters
ttl

- float
- value >= 0

timeout

- float
- value >= 0

status

- string
- valid values for update: 'active', 'released', 'revoked'

### Successful Results
Updating status from 'waiting' to 'active' without contention should:

- return HTTP 200 (OK)
- set status to 'active'
- set ttl to timeout

Updating status from 'active' to 'active' should:

- return HTTP 200 (OK)

Updating ttl while status is 'active' should:

- return HTTP 200 (OK)
- set ttl to requested value

Updating status from 'active' to 'released' should:

- return HTTP 204 (No Content)
- set status to 'released'

Updating status from 'active' or 'waiting' to 'revoked' should:

- return HTTP 204 (No Content)
- set status to 'revoked'

### Errors
- HTTP 400 (Bad Request)
    - Given unknown parameters
    - Invalid values for given parameters
- HTTP 404 (Not Found)
    - Non-existent claim
- HTTP 409 (Conflict)
    - Updating from "final" states
        - 'expired'
        - 'released'
        - 'revoked'
    - Updating from 'waiting' to 'released'
    - Updating ttl when status is not 'active'
    - Updating status from 'waiting' to 'active' with contention


## GET /v1/claims/
Filters should be specified using query strings.

Allowed filters:

- resource
- ttl
- creation time
- status


## GET /v1/claims/(id)/
### Successful Results
All successful get requests should return:

- HTTP 200 (OK)
- creation time
- metadata
- resource
- status
- (optional) status history
- timeout

Requests for 'active' claims should return:

- active duration
- ttl

Requests for 'waiting' claims should return:

- waiting duration

### Errors
- HTTP 404 (Not Found)
    - Non-existent claim
