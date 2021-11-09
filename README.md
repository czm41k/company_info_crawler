# Company INFO Crawler

## TLDR

Python script that does following:
1. Google-s provided company name to gather lsit of domains owned by company
1. Resolves the domain list to specific IPv4s
1. Grabs GEO info on IPv4s
1. Performs load_testing of each domain within locust launched via docker-compose (to increase load numbers)
    - The simplest scenario of getting a homepage is used

## Requirements

1. Internet access
1/ Docker installed

## Possible options

Use embeded helper in script to see posible options for parametrization.

> Every option has it's default value, so script can be run jsut by `python3 script.py`

## Run docker-compose by hand

`DOMAIN=domain WORKERS=<num of workers>  TIME=<seconds> USERS=<num of users for load testing> RATE=<users spawning rate for load testing> docker-compose up`

## List of possible improvements

1. Increase performance by implementing async API calls
1. EXpose Locust UI if needed
1. Workaround DNS temporary issues
1. Deal with inaccessible from test source domains

## Example of response

```shell
...
Domain is EXNESS-EX.COM
 IPv4s are: ['172.67.153.54', '104.21.34.20']
 Corresponding geo is:
 {'172.67.153.54': {'org': 'AS13335 Cloudflare, Inc.', 'city': 'San Francisco', 'country': 'US', 'region': 'California'}, '104.21.34.20': {'org': 'AS13335 Cloudflare, Inc.', 'city': 'San Francisco', 'country': 'US', 'region': 'California'}}
 Load test results available at /Users/czm41k/Documents/projects/exness_sre/exness-ex.com.html


Domain is EXNESS.ASIA
 IPv4s are: ['45.60.78.64', '45.60.133.64']
 Corresponding geo is:
 {'45.60.78.64': {'org': 'AS19551 Incapsula Inc', 'city': 'Redwood City', 'country': 'US', 'region': 'California'}, '45.60.133.64': {'org': 'AS19551 Incapsula Inc', 'city': 'Redwood City', 'country': 'US', 'region': 'California'}}
 Load test results available at /Users/czm41k/Documents/projects/exness_sre/exness.asia.html
 ...
```
