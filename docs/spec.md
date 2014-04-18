# Locking System Requirements
## Contention
- A queue of waiting claims should be kept for each `resource`.
- When a claim loses its 'active' `status`, the next claim in the queue for that
  `resource` should be changed from 'waiting' to 'active'.
- Claim `status` should be updated by the server from 'active' to 'expired'
  after that claim's `ttl` is less than 0.

## Claim Statuses
There are seven states a claim can be in at a particular time:
- 'aborted' - The client needed to abandon its claim on the resource regardless
  of whether it was 'active' or 'waiting'.  Clients should use this to cancel a
  claim in response to an error in the client.
- 'active' - This claim is the current owner of the specified resource.
- 'expired' - The client creating the claim did not update or release the claim
  before its `ttl` expired.  Ownership of the resource is likely to have been
  passed on to another claim.
- 'released' - The claim owned the resource for some time, and gave up ownership
  under normal conditions.
- 'revoked' - The claim was cancelled by an administrator or monitoring
  process.
- 'waiting' - This claim is in the queue to become the owner of its resource.
- 'withdrawn' - The client decided to withdraw its claim for the resource.

## Performance
Should support N requests per second.

- "realistic" distribution of request types should be considered
    - ~100/s PATCH requests for `status` from 'waiting' to 'active'


## Authentication & Authorization
Should require minimal effort to integrate with standard auth systems like
OAuth and Shibboleth.


## Miscellaneous Details
- times should be in seconds as floats (`ttl`, `active_duration`,
  `waiting_duration`)


## HTTP Requests

Should specify the headers:

    Content-Type: application/json
    Accepts: application/json


## POST /v1/claims/
### Parameters
Parameters should be specified in the JSON body.

`resource`

- string
- length > 0
- mandatory

`ttl`

- float
- seconds
- value >= 0
- mandatory

`user_data`

- JSON-compatible blob
- optional

### Successful Results
All successful posts should:

- set Location header
- save user-provided data
    - `user_data`
    - `resource`
    - initial `ttl`
- set automatic fields
    - `created`
    - `status`

Successful posts without contention should:

- return HTTP 201 (OK)
- set `status` to 'active'
- initialize `ttl`

Successful posts with contention should:

- return HTTP 202 (Accepted)
- set `status` to 'waiting'

### Errors
- HTTP 400 (Bad Request)
    - Missing mandatory parameters
    - Invalid values for parameters
    - Unknown parameters


## PATCH /v1/claims/(id)/
### Parameters
Parameters should be specified in the JSON body.  Only one update parameter may
be specified in a single request.

`ttl`

- float
- value >= 0

`status`

- string
- valid values for update:
    - 'aborted'
    - 'active'
    - 'released'
    - 'revoked'
    - 'withdrawn'

### Successful Results
Updating `status` from 'waiting' to 'active' without contention should:

- return HTTP 200 (OK)
- set `status` to 'active'
- initialize `ttl`

Updating `status` from 'active' to 'active' should:

- return HTTP 200 (OK)

Updating `ttl` while `status` is 'active' should:

- return HTTP 200 (OK)
- set `ttl` to requested value

Updating `status` from 'active' to 'released' should:

- return HTTP 204 (No Content)
- set `status` to 'released'

Updating `status` from 'active' or 'waiting' to a cancelled state ('aborted',
'revoked', or 'withdrawn') should:

- return HTTP 204 (No Content)
- set `status` to the requested value

### Errors
- HTTP 400 (Bad Request)
    - Given unknown parameters
    - Invalid values for given parameters
    - Updating from "final" states
        - 'aborted'
        - 'expired'
        - 'released'
        - 'revoked'
        - 'withdrawn'
    - Updating from 'waiting' to 'released'
    - Updating `ttl` when `status` is not 'active'
- HTTP 404 (Not Found)
    - Non-existent claim
- HTTP 409 (Conflict)
    - Updating `status` from 'waiting' to 'active' with contention


## GET /v1/claims/
Filters should be specified using query strings.

Allowed filters:

- `maximum_active_duration`
- `maximum_created`
- `maximum_ttl`
- `maximum_waiting_duration`
- `minimum_active_duration`
- `minimum_created`
- `minimum_ttl`
- `minimum_waiting_duration`
- `resource`
- `status`


## GET /v1/claims/(id)/
### Successful Results
All successful get requests should return:

- HTTP 200 (OK)
- `created`
- `user_data`
- `resource`
- `status`
- `status_history`

Requests for 'active' claims should return:

- `active_duration`
- `ttl`

Requests for 'waiting' claims should return:

- `waiting_duration`

### Errors
- HTTP 404 (Not Found)
    - Non-existent claim
