from json import JSONDecodeError
import backoff
import requests

class ScanStillRunningException(Exception):
    pass

class Observatory:
    def __init__(self, logger, api_url, timeout=15):
        self.api_url = api_url
        self.logger = logger
        self.timeout = timeout
        self.scan_endpoint = '{}/analyze'.format(self.api_url)

    @backoff.on_exception(backoff.expo, ScanStillRunningException, max_time=10)
    def get_scan(self, target):

        self.logger.debug('Fetching scan of target %s...', target)

        try:
            r = requests.post(url=self.scan_endpoint, params={'host': target}, headers=self.get_request_headers(),
                              timeout=self.timeout)
            if not r.ok:
                return None
        except requests.exceptions.RequestException as e:
            self.logger.fatal(e)
            self.logger.fatal('Received error from HTTP request, exiting')
            return None
        try:
            response = r.json()
            if self.is_scan_running(response):
                self.logger.debug('Scan for target %s still running (state=%s), waiting a bit and trying again', target,response.get('state'))
                raise ScanStillRunningException

            return response
        except JSONDecodeError as e:
            self.logger.fatal('API endpoint returned invalid JSON, can not parse it')
            self.logger.fatal(e)
            return None

    @staticmethod
    def is_scan_running(scan_response):
        return scan_response.get('state') in ['PENDING', 'STARTING', 'RUNNING']

    def scan(self, target):

        # Fetch a scan result from the API (trigger rescan)
        response = self.get_scan(target)

        # Sth went terribly wrong, details in logs
        if response is None:
            return None

        if 'error' in response:
            self.logger.warning(response.get('text'))
            return None

        if response.get('state') != 'FINISHED':
            self.logger.info('No score yet for target %s (state=%s), will retry later', target, response.get('state'))
            self.logger.debug(response)
            return None

        return response

    @staticmethod
    def get_request_headers():
        return {
            'Accept': 'application/json',
            'Accept-Language': 'en',
            'User-Agent': 'anroots/observatory-exporter 1.0'
        }
