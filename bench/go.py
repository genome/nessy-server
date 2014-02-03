#!/usr/bin/env python

from transitions import *
from loop import loop
from multiprocessing import Pool
from state import State

import argparse
import collections
import datetime
import itertools
import pprint


def main():
    args = parse_args()

    initial_state = State(resource_names=_resource_names(args.resources))

    transitions = [
        Activate(base_rate=args.activate_rate, get_url=args.url),
        Create(url=args.url, base_rate=args.create_rate, ttl=args.create_ttl),
        Heartbeat(base_rate=args.heartbeat_rate, ttl=args.heartbeat_ttl),
        Release(base_rate=args.release_rate),
        Revoke(base_rate=args.revoke_rate),
    ]

    pool = Pool(args.processes)
    begin = datetime.datetime.now()
    stats = pool.map(loop, itertools.repeat(
        (initial_state, transitions, args.iterations), args.processes))
    end = datetime.datetime.now()

    aggregated_reports = aggregate_reports([s.report() for s in stats])
    pprint.pprint(summarize(aggregated_reports))

    print 'total time', (end - begin).total_seconds()


def aggregate_reports(reports):
    final_report = _initial_final_report(reports)

    for report in reports:
        for action, action_data in report.iteritems():
            for method, method_data in action_data.iteritems():
                for response_code, stats in method_data.iteritems():
                    for k, v in stats.iteritems():
                        final_report[action][method][response_code][k].append(v)

    final_report = _dictify_report(final_report)

    return final_report


def _initial_final_report(reports):
    return collections.defaultdict(
            lambda: collections.defaultdict(
                lambda: collections.defaultdict(
                    lambda: collections.defaultdict(list))))


def _dictify_report(report):
    result = {}
    for k0, v0 in report.iteritems():
        result[k0] = {}
        for k1, v1 in v0.iteritems():
            result[k0][k1] = {}
            for k2, v2 in v1.iteritems():
                result[k0][k1][k2] = dict(v2)

    return result



def _mean(items):
    return sum(items) / len(items)

_STAT_SUMMARY_METHODS = {
    'count': sum,
    'min': min,
    'max': max,
    'median': _mean,
    'mean': _mean,
    'rps': sum,
}

def summarize(report):
    result = {}
    total_data = collections.defaultdict(list)
    for action, action_data in report.iteritems():
        result[action] = {}
        for method, method_data in action_data.iteritems():
            result[action][method] = {}
            for response_code, stats in method_data.iteritems():
                result[action][method][response_code] = {}
                for stat_name, values in stats.iteritems():
                    stat_method = _STAT_SUMMARY_METHODS[stat_name]
                    sv = stat_method(values)
                    result[action][method][response_code][stat_name] = sv
                    total_data[stat_name].append(sv)

    result['Total'] = _compute_total_summary(total_data)

    return result


def _compute_total_summary(total_data):
    result = {}
    count = sum(total_data['count'])
    result['count'] = count
    result['min'] = min(total_data['min'])
    result['max'] = max(total_data['max'])
    result['mean'] = _weighted_mean(total_data['mean'], total_data['count'])
    result['rps'] = _weighted_mean(total_data['rps'], total_data['count'])
    return result

def _weighted_mean(values, weights):
    total_value = 0
    total_weight = 0
    for v, w in itertools.izip(values, weights):
        total_value += v * w
        total_weight += w
    return total_value / total_weight


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('url', default='http://localhost:5000/v1/claims/',
            nargs='?', help='URL for POSTing new claims')

    parser.add_argument('-i', '--iterations', type=int, default=1000,
            help='Number of requests to make per process')
    parser.add_argument('-p', '--processes', type=int, default=1,
            help='Number of processes')

    parser.add_argument('-r', '--resources', type=int, default=10,
            help='Number of resources to lock')

    transition_parameters = parser.add_argument_group('Transition Parameters')
    transition_parameters.add_argument('--activate-rate', type=float, default=1)

    transition_parameters.add_argument('--create-rate', type=float, default=1)
    transition_parameters.add_argument('--create-ttl', type=float, default=1)

    transition_parameters.add_argument('--heartbeat-rate', type=float,
            default=5)
    transition_parameters.add_argument('--heartbeat-ttl', type=float, default=1)

    transition_parameters.add_argument('--release-rate', type=float, default=1)
    transition_parameters.add_argument('--revoke-rate', type=float, default=1)

    return parser.parse_args()


def _resource_names(num_resources):
    return ['bench-resource-%d' % i for i in xrange(num_resources)]


if __name__ == '__main__':
    main()
