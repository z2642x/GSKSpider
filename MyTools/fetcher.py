from threading import Thread, Lock
from queue import Queue
from MyTools.tools import URLTool
import urllib.request
import urllib.error
import socket
import random
import time
import logging


class Fetcher:
    __AGENT_LIST = [
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
        "Opera/9.25 (Windows NT 5.1; U; en)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12",
        "Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9",
        "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 "
        "Chrome/16.0.912.77 Safari/535.7",
        "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 "
        "Safari/537.36 SE 2.X MetaSr 1.0"
    ]

    __PROXY_LIST = [
        ("91.216.72.209", "8080"),
        ("200.229.225.54", "80"),
        ("5.56.16.165", "3128"),
        ("172.99.73.23", "3128"),
        ("80.34.223.19", "3128"),
        ("37.218.152.156", "3128"),
        ("204.29.120.89", "21320"),
        ("187.177.14.104", "8080"),
        ("92.42.163.198", "3128"),
        ("179.183.102.203", "8080"),
        ("183.88.84.49", "3128"),
        ("45.32.43.97", "80"),
        ("95.167.116.115", "8080"),
        ("207.172.128.240", "3128"),
        ("222.1.247.149", "8080"),
        ("146.184.0.115", "80"),
        ("37.188.72.122", "80"),
        ("112.78.178.19", "8080"),
        ("193.242.164.85", "3128"),
        ("58.11.75.14", "8080"),
        ("14.63.68.73", "8081"),
        ("187.32.163.97", "3128"),
        ("61.7.149.69", "8080"),
        ("146.185.253.241", "3128"),
        ("172.99.73.14", "3128"),
        ("180.249.224.253", "8080"),
        ("80.219.16.3", "6666"),
        ("189.218.13.67", "8088"),
        ("200.92.81.122", "8090"),
        ("121.78.195.165", "8888"),
        ("36.79.251.99", "3128"),
        ("125.167.112.233", "8080"),
        ("177.234.12.202", "3128"),
        ("83.128.190.244", "80"),
        ("108.165.33.7", "3128"),
        ("81.162.237.229", "8182"),
        ("193.172.85.233", "80"),
        ("118.96.69.57", "3128"),
        ("84.180.226.171", "8080"),
        ("82.101.220.241", "80"),
        ("197.44.62.18", "3128"),
        ("125.26.179.25", "8080"),
        ("164.132.11.206", "3128"),
        ("14.49.164.71", "808"),
        ("193.138.239.140", "8080"),
        ("220.123.135.83", "8080"),
        ("5.56.16.246", "3128"),
        ("144.122.175.164", "8080"),
        ("172.99.73.42", "3128"),
        ("201.54.5.115", "8080"),
        ("183.89.201.40", "8080"),
        ("113.171.0.46", "3128"),
        ("31.18.147.178", "80"),
        ("144.122.165.15", "8080"),
        ("125.253.122.110", "3128"),
        ("219.92.196.178", "80"),
        ("89.19.176.118", "80"),
        ("108.75.86.149", "3128"),
        ("177.74.149.93", "8088"),
        ("36.80.126.98", "8080"),
        ("187.44.14.249", "8080"),
        ("52.53.185.46", "8080"),
        ("58.11.24.199", "8888"),
        ("188.166.229.243", "8080"),
        ("138.201.70.133", "3128"),
        ("222.236.1.6", "8081"),
        ("94.205.81.171", "80"),
        ("64.128.31.29", "3128"),
        ("177.92.56.11", "8080"),
        ("85.25.246.196", "3128"),
        ("14.139.213.183", "3128"),
        ("89.239.128.150", "80"),
        ("94.76.201.108", "80"),
        ("137.117.227.221", "3128"),
        ("91.98.118.178", "8080"),
        ("201.172.246.226", "8088"),
        ("208.89.215.102", "80"),
        ("217.170.197.99", "3128"),
        ("188.186.16.197", "8080"),
        ("94.23.21.195", "8118"),
        ("183.89.83.114", "3128"),
        ("80.57.110.15", "80"),
        ("1.244.116.171", "8000"),
        ("190.122.184.85", "8080"),
        ("103.18.4.83", "3128"),
        ("212.38.166.231", "443"),
        ("113.53.91.216", "8080"),
        ("36.82.40.62", "8080"),
        ("187.161.147.111", "8088"),
        ("52.91.206.104", "8080"),
        ("186.112.231.186", "8080"),
        ("124.120.120.229", "3128"),
        ("128.199.126.82", "8080"),
        ("179.222.109.63", "3128"),
        ("110.171.26.21", "8080"),
        ("149.202.249.227", "3128"),
        ("213.230.18.191", "8080"),
        ("185.50.215.116", "8080"),
        ("89.101.214.214", "8080"),
        ("177.43.179.195", "3128"),
    ]

    def __init__(self, threads_num=1, opener=None, interval=10):
        if opener is None:
            self.__opener = urllib.request.build_opener()
        else:
            self.__opener = opener
        self.cookie = False
        self.__lock = Lock()
        self.__job_queue = Queue()
        self.__result_queue = Queue()
        self.__threads_num = threads_num
        self.__interval = interval
        for i in range(threads_num):
            t = Thread(target=self.fetch)
            t.setDaemon(True)
            t.start()
        self.__running_num = 0

    def __del__(self):
        time.sleep(0.5)
        self.__job_queue.join()
        self.__result_queue.join()

    def push_bunch(self, queue):
        for job in queue:
            if isinstance(job, str):
                self.push(job)
            elif isinstance(job, tuple):
                if len(job) > 1:
                    self.push(job[0])
                elif len(job) == 1:
                    self.push(job[0], job[1])

    def push(self, url, data=None):
        self.__job_queue.put((url, data))

    def pop(self):
        return self.__result_queue.get()

    def taskleft(self):
        return self.__job_queue.qsize() + \
               self.__result_queue.qsize() + \
               self.__running_num

    def reset_agent(self):
        agent = random.choice(self.__AGENT_LIST)
        new_headers = []
        for key, value in self.__opener.addheaders:
            if key.lower() == "user-agent":
                value = agent
            header = (key, value)
            new_headers.append(header)
        self.__opener.addheaders = new_headers

    def fetch(self):
        while True:
            time.sleep(random.uniform(self.__interval, self.__interval * 3))
            url, data = self.__job_queue.get()
            with self.__lock:
                self.__running_num += 1

            try:
                self.reset_agent()
                ip, port = random.choice(self.__PROXY_LIST)
                logging.info("    Fetcher is fetching content from %s" % url)
                self.__opener = URLTool.get_url_opener(self.__opener.addheaders, ip, port, self.cookie)
                content = URLTool.get_page_content(self.__opener, url, data)
            except ConnectionResetError:
                print("    Fetcher: ConnectionResetError occured.")
                content = ""
            except urllib.error.HTTPError as e:
                print("    Fetcher: HTTPError occured.")
                print(e)
                content = ""
                # print("    Trying to rebuild opener")
                # self.reset_agent()
                # self.cookie = not self.cookie
                # ip, port = random.choice(self.__PROXY_LIST)
                # self.__opener = URLTool.get_url_opener(self.__opener.addheaders, ip, port, self.cookie)
                # self.__opener = URLTool.get_url_opener(self.__opener.addheaders, need_cookie=self.cookie)
                # self.__job_queue.put((url, data))
                # time.sleep(random.uniform(self.__interval, self.__interval + 5))
            except urllib.error.URLError:
                print("    Fetcher: URLError occured.")
                content = ""
            except socket.timeout:
                print("    Fetcher: Timeout occured.")
                content = ""
            finally:
                self.__result_queue.put((url, content))
                with self.__lock:
                    self.__running_num -= 1
                self.__job_queue.task_done()


if __name__ == "__main__":
    links = [('http://www.verycd.com/topics/%d/' % i) for i in range(5420, 5450)]
    f = Fetcher(threads_num=10, interval=1)

    f.push_bunch(links)
    while f.taskleft():
        addr, pageContent = f.pop()
        print(addr, len(pageContent))
