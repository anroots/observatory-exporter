import sys
from prometheus_client import start_http_server, Summary
import time
from prometheus_client.core import REGISTRY
import logging
import os
from prometheus_client.metrics_core import GaugeMetricFamily

from src.lib.observatory import Observatory

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO'),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('observatory-exporter')


class ObservatoryCollector(object):
    def __init__(self, api_url, targets):
        self.observatory = Observatory(logger, api_url)
        self.targets = targets

    @REQUEST_TIME.time()
    def collect(self):
        logger.info('Starting scrape')

        for target in self.targets:

            scan_results = self.observatory.scan(target)

            if not scan_results:
                logger.warning('Did not get scan results for target %s, skipping it', target)
                continue

            gauge = GaugeMetricFamily("http_observatory_score", 'Numerical overall score from Observatory',
                                      labels=['target', 'grade', 'scan_time'])

            gauge.add_metric([target, scan_results.get('grade'), scan_results.get('end_time')],
                             scan_results.get('score', 0))
            yield gauge

            gauge = GaugeMetricFamily("http_observatory_tests", 'Number of tests run by the Observatory',
                                      labels=['target', 'type'])

            gauge.add_metric([target, 'failed'], scan_results.get('tests_failed'))
            gauge.add_metric([target, 'passed'], scan_results.get('tests_passed'))
            gauge.add_metric([target, 'quantity'], scan_results.get('tests_quantity'))

            yield gauge

            logger.info('%s received score of %d on %s', target, scan_results.get('score'),
                        scan_results.get('end_time'))

        logger.info('Scraping completed')


if __name__ == '__main__':
    logger.info('observatory-exporter (https://github.com/anroots/observatory-exporter) starting up...')
    api_url = os.environ.get('OBSERVATORY_API_URL', 'https://http-observatory.security.mozilla.org/api/v1')

    targets = os.environ.get('OBSERVATORY_TARGETS', '').strip()
    if not targets:
        logger.fatal('No targets to scan, please set environment variable OBSERVATORY_TARGETS')
        sys.exit(1)

    REGISTRY.register(ObservatoryCollector(api_url, targets.split(',')))
    start_http_server(8080)
    logger.info('Collector started, listening on port :8080; waiting for scrapes...')

    while True:
        time.sleep(1)
