import csv
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
from locust import HttpUser, SequentialTaskSet, task, between
from locust.env import Environment
from locust.stats import stats_printer, stats_history
from locust.log import setup_logging
from http.client import error


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


# def check_site_performance(d: dict) -> dict:
#   for domain in d:
#     r = load_test(domain,ui=True)
#     d[domain]['tech_attributes'] = r



def load_test(summary: dict, host_header: str, ui: bool, users:int=1, time:int()=60) -> dict:
  for domain in summary:
    print(f"DOMAIN NOW {domain}")
    # for ip in domain:
    target_host = f"https://{domain}"
    env = Environment(user_classes=[User],host=target_host)
    env.create_local_runner()
    if ui:
      env.create_web_ui('127.0.0.1', 8089)
    gevent.spawn(stats_printer(env.stats))
    gevent.spawn(stats_history, env.runner)
    # start the test
    env.runner.start(1,1,wait=True)
    gevent.spawn_later(10, lambda: env.runner.quit())
    env.runner.greenlet.join()
    if ui:
      env.web_ui.stop()
    # print(f"{stats_history=}")
    print(f"{env.runner.environment=}")
      


# class MyEnv(Environment):


# class UserBehaviour(SequentialTaskSet):
#   def on_start(self):
#     self.client.verify = True

#   @task
#   def my_task(self):
#       with self.client.get("/") as get_resp:
#         # print(f"{get_resp.headers=}")
#         print(get_resp)
#         # print(get_resp.text)
#         print(get_resp.url)


# class User(HttpUser):
#   tasks = [UserBehaviour]
#   wait_time = between(1,2)

#   # def __init__(self, *args, **kwargs):
#   #   HttpUser.__init__(self, *args, **kwargs)
#   #   if 'host-header' in kwargs:
#   #     self.host_header = kwargs['host_header']




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
    load_test(summary, host_header, ui=True, users=5,time=30)
  # for cip in custom_ips:

