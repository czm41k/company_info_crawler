import csv
import subprocess
from collections.abc import Sequence
import json
from warnings import catch_warnings
import gevent
from gevent.events import IPeriodicMonitorThread
import gevent.monkey
gevent.monkey.patch_all() # needed due to https://github.com/gevent/gevent/issues/1016 and causing recursion error for ssl endpoints
import urllib.error
import dns.resolver
from urllib.request import urlopen
from googlesearch import search



def to_csv(d: dict, output: str) -> None:
  with open(f"{output}.csv",'w') as f:
    w = csv.DictWriter(f, d.keys())
    w.writeheader()
    w.writerow(d)


def get_domains(site_name: str, depth: int, pause: int) -> set:
  """Gets incoming company name
  Google for matches
  Returns a list of domain names found
  """
  results = set()
  query_by_site = f"site: {site_name}"
  try:
    for r in search(query_by_site,stop=depth,pause=pause):
      r = str(r).split(':')[1] # cutting off protocol
      url = r[2:].split('/')[0] # cutting off path
      url = url.split('.',1)[1]if site_name not in url.split('.')[0] else url
      if site_name in url:
        results.add(url) # Adding only if site_name still exists as substring
  except urllib.error.HTTPError:
    print("Google API denies due to too many requests. Try to wait for a while and proceed with pause value increased")
  return results


def get_endpoints(domains: set) -> dict:
  """Resolving provided list of domains to theirA records
  Returns a dict with list of IPv4 for each domain given
  """
  endpoints = {}
  for site in domains:
    ips = []
    for rdata in dns.resolver.resolve(site,'A'):
      ips.append(str(rdata))
    endpoints[site] = ips
  return endpoints


def get_geo(ips: list, name: str) -> dict:
  """Gets incoming list of IPv4s
  Returns geo information for each of them in dict
  """
  results = {}
  for ip in ips:
    result= {}
    print(ip)
    url = f"http://ipinfo.io/{ip}/json"
    response = urlopen(url)
    data = json.load(response)
    # result['ip'] = data['ip']
    result = {
      'org': data['org'],
      'city': data['city'],
      'country': data['country'],
      'region': data['region']
      }
    results[ip]=result
    # print(f"{data['ip']=} {data['region']=} {data['country']=} {data['city']=} {data['org']=}")
  return {name: results}


def load_test(summary: dict, users:int=1000, time:int()=15) -> dict:
  for domain in summary:
    print(f"DOMAIN NOW {domain}")
    test = subprocess.Popen(f"DOMAIN={domain}  WORKERS=3 TIME={time} USERS={users} RATE={users // 4} docker-compose up",
      check=True, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    test_result = test.stdout
    test.wait()
    print(f"Finished for {domain} with results \n{test_result=}")



if __name__ == "__main__":
  domains = get_domains('exness',10,5)
  print(f"{domains=}")
  endpoints = get_endpoints(domains)
  host_header = str()
  print(f"{endpoints=}")
  for row in endpoints:
    print(row)
    summary = get_geo(endpoints[row],row)
    print(f"{summary=}")
    load_test(summary,users=5,time=30)

