import collections


class TimeCollection(object):
    def __init__(self):
        self.times = []
        self.min_time = None
        self.max_time = None
        self.total_time = 0

    @property
    def count(self):
        return len(self.times)

    @property
    def mean_time(self):
        if self.times:
            return self.total_time / len(self.times)

    @property
    def median_time(self):
        self.times.sort()

        len_m_1 = len(self.times) - 1
        if len_m_1 % 2 == 0:
            return self.times[len_m_1/2]
        else:
            return (self.times[int(len_m_1)/2]
                    + self.times[len(self.times)/2]) / 2

    def add_time(self, time):
        if self.min_time is None or time < self.min_time:
            self.min_time = time
        if self.max_time is None or time > self.max_time:
            self.max_time = time

        self.total_time += time
        self.times.append(time)


class Stats(object):
    def __init__(self):
        self._data = collections.defaultdict(TimeCollection)

    def add_request(self, action, method, response_code, time):
        self._data[(action, method, response_code)].add_time(time)

    def report(self):
        results = collections.defaultdict(
                lambda: collections.defaultdict(dict)
        )
        for (action, method, response_code), times in self._data.iteritems():
            results[action][method][response_code] = {
                    'count': times.count,
                    'min': times.min_time,
                    'max': times.max_time,
                    'mean': times.mean_time,
                    'median': times.median_time,
                    'rps': 1 / times.mean_time,
            }

        return self._dictify_report(results)

    def _dictify_report(self, report):
        result = {}
        for k, v in report.iteritems():
            result[k] = dict(v)
        return result
