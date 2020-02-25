# observatory-exporter

A custom [Prometheus exporter][] for exporting metrics from [Mozilla Observatory][] scanner.

_N.B! Current version of this exporter is unstable; and with not a lot of error handling.
It was thrown together for an immediate need. Needs more development to become stable._

## Usage

This is designed to be run in a Docker container. Deploy it to your Docker platform of choice.
The exporter will listen on port `8080`.

```bash
$ docker run -p 8080:8080 -e anroots/observatory-exporter
```

Configure a new Prometheus target to scrape the exposed endpoint.

```yaml
scrape_configs:
  - job_name: 'observatory-exporter'
    scrape_interval: 24h
    static_configs:
      - targets:
        - observatory-exporter:8080
 
```

The following metrics will be saved:

```
# HELP http_observatory_score Numerical overall score from Observatory
# TYPE http_observatory_score gauge
http_observatory_score{target="jaa.ee"} 60.0
# HELP http_observatory_tests Number of tests run by the Observatory
# TYPE http_observatory_tests gauge
http_observatory_tests{target="jaa.ee",type="failed"} 3.0
http_observatory_tests{target="jaa.ee",type="passed"} 9.0
http_observatory_tests{target="jaa.ee",type="quantity"} 12.0
```


### Environment variables

| Variable name | Description | Default value | Required | 
| ------------- | ----------- | ------------- | -------- |
| OBSERVATORY_API_URL | HTTPS URL to the observatory API. Default is to use Mozilla hosted API, but you can also deploy your own scanner. | `https://http-observatory.security.mozilla.org/api/v1` | No |
| OBSERVATORY_TARGETS | Comma-separated list of domains to scan using the exporter (example: `jaa.ee,mozilla.com`)|`None`| Yes |
| LOG_LEVEL| Exporter log level (to stdout)| `INFO` | No |


## Development

Use the included `docker-compose.yml` file for development..

```bash
$ docker-compose up
```

...or install dependencies to Python venv, and debug locally:

```bash
$ pip install -r requirements.txt
$ python src/collector.py
```


## References

- [Mozilla Observatory API doc](https://github.com/mozilla/http-observatory/blob/master/httpobs/docs/api.md)
- [Run your own scanner](https://github.com/mozilla/http-observatory)
- [Alternate exporter, doesn't seem to work](https://github.com/Jimdo/observatory-exporter/)

[Prometheus exporter]: https://prometheus.io/docs/instrumenting/writing_exporters/
[Mozilla Observatory]: https://observatory.mozilla.org
