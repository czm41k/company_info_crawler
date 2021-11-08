from subprocess import call,PIPE,CalledProcessError
import os
import argparse
import json
import dns.resolver
import urllib.error
from urllib.request import urlopen
from googlesearch import search


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


class CompanyInstance():
  def __init__(self, domain):
    self.domain = domain
    self.args = self._parse_args()
    self.ipv4s = self._get_endpoints(self.domain)
    self.geo = self._get_geo()
    self._load_test()

  def _parse_args(self) -> dict:
        parser = argparse.ArgumentParser(description=f"Web crawler. Gather all INFO on provided domain")
        parser.add_argument('-u', action='store', dest='load_users', type=int, default=1000, help='Count of users for Locust load testing')
        parser.add_argument('-t', action='store', dest='load_time', type=int, default=15, help="Time in seconds to run Locust load test")
        args = parser.parse_args()
        return args

  def __str__(self) -> None:
    return f"domain is {self.domain.upper()}\n IPv4s are: {self.ipv4s}\n Corresponding geo is:\n {self.geo}\n Load test results available at {self.report_link}"


  def _get_endpoints(self, domain: str) -> list:
    """Resolving provided list of domains to theirA records
    Returns a dict with list of IPv4 for each domain given
    """
    ips = []
    for rdata in dns.resolver.resolve(domain,'A'):
      ips.append(str(rdata))
    return ips


  def _get_geo(self) -> dict:
    """Gets incoming list of IPv4s
    Returns geo information for each of them in dict
    """
    results = {}
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


  def _load_test(self) -> dict:
    print("Starting load test")
    spawning_rate = self.args.load_users // 4 if self.args.load_users > 100 else self.args.load_users
    cmd = f"cd code && DOMAIN={self.domain} WORKERS=3 TIME={self.args.load_time} USERS={self.args.load_users} RATE={spawning_rate} docker-compose up"
    print(f"DOMAIN NOW {self.domain}. Running load test within \n {cmd=}")
    test = call(cmd,stdout=PIPE, universal_newlines=True, shell=True, timeout=self.args.load_time*2)
    # print('waiting')
    print(f"Finished for {self.domain} with exit code {test.wait()}, all stats generated to {self.domain}.html report locally")
    self.report_link = f"{os. getcwd()}/{self.domain}.html"


if __name__ == "__main__":
  domains = get_domains('exness',10,5)
  for domain in domains:
    instance = CompanyInstance(domain)
    print(instance)
