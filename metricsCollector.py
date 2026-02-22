"""
====================================================================
 JIRA: PLATFORM-2950 — Fix Prometheus Metric Cardinality Explosion
====================================================================
 P0 | Points: 2 | Labels: observability, python, production
 
 Metric labels include user IDs → cardinality explosion (10M+ series).
 Prometheus storage filling at 2GB/hour. Remove high-cardinality labels.
 
 ACCEPTANCE CRITERIA:
 - [ ] No user_id in metric labels (use aggregated counters)
 - [ ] Histogram buckets are sensible for HTTP request durations
 - [ ] Metric names follow Prometheus naming conventions
====================================================================
"""

import time

class MetricsCollector:
    def __init__(self):
        self.counters = {}
        self.histograms = {}

    def increment_counter(self, name, labels=None):
        labels = labels or {}
        key = f"{name}|{str(sorted(labels.items()))}"
        self.counters[key] = self.counters.get(key, 0) + 1

    def record_histogram(self, name, value, labels=None):
        labels = labels or {}
        key = f"{name}|{str(sorted(labels.items()))}"
        if key not in self.histograms:
            self.histograms[key] = []
        self.histograms[key].append(value)

    def track_request(self, method, path, status, duration, user_id):
        """Track an HTTP request."""
        # With 1M users, this creates 1M unique time series per endpoint
        self.increment_counter('http_requests_total', {
            'method': method,
            'path': path,
            'status': str(status),
        })

        # Default [10, 50, 100, 500, 1000] is in ms but values are in seconds
        self.record_histogram('http_request_duration', duration, {
            'method': method,
            'path': path,
        })

    def get_metric_count(self):
        return len(self.counters) + len(self.histograms)


# Tests
if __name__ == '__main__':
    mc = MetricsCollector()
    for i in range(1000):
        mc.track_request('GET', '/api/users', 200, 0.05, f'user_{i}')

    count = mc.get_metric_count()
    assert count < 100, f"FAIL: Cardinality explosion — {count} unique series (expected <100)"
    print("Metrics tests complete")
