import subprocess
import os
import argparse
import json
import dns.resolver
import dns.exception
import urllib.error
from urllib.request import urlopen
from googlesearch import search
from typing import Union


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


def parse_args() -> dict:
  parser = argparse.ArgumentParser(description=f"Web crawler. Gather all INFO on provided domain")

  parser.add_argument('-c', '--company', action='store', dest='company', type=str, default='exness', help='Name of company to gather info')
  parser.add_argument('-u', action='store', dest='load_users', type=int, default=1000, help='Count of users for Locust load testing')
  parser.add_argument('-t', action='store', dest='load_time', type=int, default=15, help="Time in seconds to run Locust load test")
  parser.add_argument('-d', action='store', dest='google_depth', type=int, default=10, help="Depth of search for domain matches (Googling depth)")
  parser.add_argument('-gt', '--googling-timeout', action='store', dest='google_timeout', type=int, default=5, help="Time (in secs) between 2 consequent google API requests")
  args = parser.parse_args()
  return args


class CompanyInstance():
  def __init__(self, domain):
    self.domain = domain
    self.ipv4s = self._get_endpoints(self.domain)
    self.geo = self._get_geo()
    self.report_link = str()


  def __str__(self) -> None:
    return f"Domain is {self.domain.upper()}\n IPv4s are: {self.ipv4s}\n Corresponding geo is:\n {self.geo}\n Load test results available at {self.report_link}\n\n"


  def _get_endpoints(self, domain: str) -> Union[list,None]:
    """Resolving provided list of domains to theirA records
    Returns a dict with list of IPv4 for each domain given
    """
    ips = []
    try:
      for rdata in dns.resolver.resolve(domain,'A'):
        ips.append(str(rdata))
      return ips
    except dns.exception.Timeout as e:
      print(f"Failed to determine IPs using default ")
      return None


  def _get_geo(self) -> Union[dict,None]:
    """Gets incoming list of IPv4s
    Returns geo information for each of them in dict
    """
    results = {}
    if isinstance(self.ipv4s,list):
      for ip in self.ipv4s:
        result= {}
        url = f"http://ipinfo.io/{ip}/json"
        response = urlopen(url)
        data = json.load(response)
        result = {
          'org': data['org'],
          'city': data['city'],
          'country': data['country'],
          'region': data['region']
          }
        results[ip]=result
      return results
    else:
      return None


def load_test(domain: str,users_count: int,test_length: int) -> str:
  """Performs load testing using Locust tool 
  Launched within docker-compose"""
  print("Starting load test")
  spawning_rate = users_count // 4 if users_count > 100 else users_count
  cmd = f"cd code && DOMAIN={domain} WORKERS=3 TIME={test_length} USERS={users_count} RATE={spawning_rate} docker-compose up"
  print(f"DOMAIN NOW {domain}. Running load test within \n {cmd=}")
  # Executing load test in separate process
  for path in execute(cmd):
    print(path,end="")

  print(f"Finished for {domain}")
  return f"{os. getcwd()}/{domain}.html"


def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True,shell=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    popen.wait()


def main():
  args = parse_args()
  instances = []
  domains = get_domains(args.company,args.google_depth,args.google_timeout)
  for domain in domains:
    instance = CompanyInstance(domain)
    instance.report_link = load_test(domain, args.load_users, args.load_time)
    instances.append(instance)
  [print(i) for i in instances]
  print(domains)


if __name__ == "__main__":
  main()
