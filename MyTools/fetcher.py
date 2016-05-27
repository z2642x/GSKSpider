from threading import Thread, Lock
from queue import Queue
from MyTools.tools import URLTool
import urllib.parse
import urllib.request
import urllib.error
import socket
import random
import time
import logging


class Fetcher:

    def __init__(self, threads_num=1, opener=None, interval=10):
        if opener is None:
            self.__opener = urllib.request.build_opener()
        else:
            self.__opener = opener
        self.cookie = True
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

    def fetch(self):
        while True:
            time.sleep(random.uniform(self.__interval, self.__interval * 3))
            url, data = self.__job_queue.get()
            with self.__lock:
                self.__running_num += 1

            try:
                content = URLTool.get_page_content(self.__opener, url, data)
            except ConnectionResetError:
                print("    Fetcher: ConnectionResetError occured when opening %s" % url)
                content = ""
            except urllib.error.HTTPError as e:
                print("    Fetcher: HTTPError occured when opening %s" % url)
                print(e)
                content = ""
            except urllib.error.URLError:
                print("    Fetcher: URLError occured when opening %s" % url)
                content = ""
            except socket.timeout:
                print("    Fetcher: Timeout occured when opening %s" % url)
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
