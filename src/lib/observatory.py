from json import JSONDecodeError

import requests
import sys


class Observatory:
    def __init__(self, logger, api_url, timeout = 15):
        self.api_url = api_url
        self.logger = logger
        self.timeout = timeout

    def scan(self, target):

        self.logger.info('Starting scan of target %s...', target)

        scan_endpoint = '{}/analyze'.format(self.api_url)

        try:
            r = requests.post(url=scan_endpoint, params={'host':target, 'rescan': 'true'}, headers=self.get_request_headers(), timeout=self.timeout)
            if not r.ok:
                return None
        except requests.exceptions.RequestException as e:
            self.logger.fatal(e)
            self.logger.fatal('Received error from HTTP request, exiting')
            sys.exit(1)
        try:
            response = r.json()
        except JSONDecodeError as e:
            self.logger.fatal('API endpoint returned invalid JSON, can not parse it')
            self.logger.fatal(r.text)
            sys.exit(1)
        if 'error' in response:
            self.logger.warning(response.get('text'))
            return None
        return response

    @staticmethod
    def get_request_headers():
        return {
            'Accept': 'application/json',
            'Accept-Language': 'en',
            'User-Agent': 'anroots/observatory-exporter 1.0'
        }




