from locust import HttpUser, SequentialTaskSet, task, between
from locust.env import Environment
from locust.stats import stats_printer, stats_history
from locust.log import setup_logging
from http.client import error


class UserBehaviour(SequentialTaskSet):
  def on_start(self):
    self.client.verify = True
  @task
  def my_task(self):
      with self.client.get("/") as get_resp:
        # print(f"{get_resp.headers=}")
        print(get_resp)
        # print(get_resp.text)
        print(get_resp.url)


class User(HttpUser):
  tasks = [UserBehaviour]
  wait_time = between(1,2)

  # def __init__(self, *args, **kwargs):
  #   HttpUser.__init__(self, *args, **kwargs)
  #   if 'host-header' in kwargs:
  #     self.host_header = kwargs['host_header']
