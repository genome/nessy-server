from . import models
import datetime


def resource_equal(query, resource):
    if resource is not None:
        return query.filter_by(resource=resource)
    else:
        return query


def status_equal(query, status):
    if status is not None:
        return query.filter_by(status=status)
    else:
        return query


def active_duration_range(query, minimum_active_duration,
        maximum_active_duration):
    if minimum_active_duration is not None:
        minimum_active_duration = datetime.timedelta(
                seconds=minimum_active_duration)
        finished_claims = query.filter(
                models.Claim._done_active_duration != None,
                models.Claim._done_active_duration
                    >= minimum_active_duration)
        active_claims = query.filter(
                models.Claim._live_active_duration != None,
                models.Claim._live_active_duration
                    >= minimum_active_duration)
        query = finished_claims.union(active_claims)

    if maximum_active_duration is not None:
        maximum_active_duration = datetime.timedelta(
                seconds=maximum_active_duration)
        finished_claims = query.filter(
                models.Claim._done_active_duration != None,
                models.Claim._done_active_duration
                    <= maximum_active_duration)
        active_claims = query.filter(
                models.Claim._live_active_duration != None,
                models.Claim._live_active_duration
                    <= maximum_active_duration)
        query = finished_claims.union(active_claims)

    return query


def waiting_duration_range(query, minimum_waiting_duration,
        maximum_waiting_duration):
    if minimum_waiting_duration is not None:
        minimum_waiting_duration = datetime.timedelta(
                seconds=minimum_waiting_duration)
        activated_claims = query.filter(
                models.Claim.activated != None,
                models.Claim._done_waiting_duration
                    >= minimum_waiting_duration)

        deactivated_claims = query.filter(
                models.Claim.activated == None,
                models.Claim.deactivated != None,
                models.Claim._skip_waiting_duration
                    >= minimum_waiting_duration)

        currently_waiting_claims = query.filter(
                models.Claim.activated == None,
                models.Claim.deactivated == None,
                models.Claim._still_waiting_duration
                    >= minimum_waiting_duration)

        query = activated_claims.union(deactivated_claims,
                currently_waiting_claims)

    if maximum_waiting_duration is not None:
        maximum_waiting_duration = datetime.timedelta(
                seconds=maximum_waiting_duration)
        activated_claims = query.filter(
                models.Claim.activated != None,
                models.Claim._done_waiting_duration
                    <= maximum_waiting_duration)

        deactivated_claims = query.filter(
                models.Claim.activated == None,
                models.Claim.deactivated != None,
                models.Claim._skip_waiting_duration
                    <= maximum_waiting_duration)

        currently_waiting_claims = query.filter(
                models.Claim.activated == None,
                models.Claim.deactivated == None,
                models.Claim._still_waiting_duration
                    <= maximum_waiting_duration)

        query = activated_claims.union(deactivated_claims,
                currently_waiting_claims)

    return query
