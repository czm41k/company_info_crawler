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

## TODO List

1. Increase performance by implementing async API calls
1. EXpose Locust UI if needed
1. Workaround DNS temporary issues