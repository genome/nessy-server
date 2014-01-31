#!/usr/bin/env python

from transitions import *
from loop import loop
from multiprocessing import Pool
from state import State

import argparse
import datetime
import itertools
import pprint


def main():
    args = parse_args()

    initial_state = State(resource_names=_resource_names(args.resources))

    transitions = [
        Activate(base_rate=args.activate_rate),
        Create(url=args.url, base_rate=args.create_rate, ttl=args.create_ttl),
        Heartbeat(base_rate=args.heartbeat_rate, ttl=args.heartbeat_ttl),
        Release(base_rate=args.release_rate),
        Revoke(base_rate=args.revoke_rate),
    ]

    pool = Pool(args.processes)
    begin = datetime.datetime.now()
    final_states = pool.map(loop, itertools.repeat(
        (initial_state, transitions, args.iterations), args.processes))
    end = datetime.datetime.now()

    for fs in final_states:
        results = fs.report()
        pprint.pprint(results)

    print 'total time', (end - begin).total_seconds()


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
    transition_parameters.add_argument('--activate-rate', type=float,
            default=50)

    transition_parameters.add_argument('--create-rate', type=float, default=100)
    transition_parameters.add_argument('--create-ttl', type=float, default=1)

    transition_parameters.add_argument('--heartbeat-rate', type=float,
            default=5)
    transition_parameters.add_argument('--heartbeat-ttl', type=float, default=1)

    transition_parameters.add_argument('--release-rate', type=float, default=2)
    transition_parameters.add_argument('--revoke-rate', type=float, default=1)

    return parser.parse_args()


def _resource_names(num_resources):
    return ['bench-resource-%d' % i for i in xrange(num_resources)]


if __name__ == '__main__':
    main()
