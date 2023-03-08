import requests
import random
import time
import threading
import warnings
from urllib3.exceptions import InsecureRequestWarning

from web_analysis import WebAnalysis
from proxies import ProxyOperations
import constants as const


"""========================================================================================================="""
"""========================================================================================================="""
"""========================================================================================================="""
"""SQL Injection onto the website"""


class SQLAnalysis:
    def __init__(self):
        self.__payload_gen = (row.rstrip() for row in
                              open(const.SQL_PAYLOAD_WORDLIST, "r"))
        warnings.simplefilter("ignore", InsecureRequestWarning)
        self.__proxy = {}
        self.__headers = {}
        self.__request_obj_time = []
        self.__stage2_results = []

    """======================================================================================================"""
    """Creating and checking request objects"""

    # Thread sends request with proxy
    def request_proxy(self, link, stage):
        try:
            self.__headers = {"User-agent": random.choice(const.USER_AGENTS)}
            time.sleep(self.__create_delay())
            time_request = time.time()
            response = requests.get(link, proxies=self.__proxy, headers=self.__headers, verify=False)
            if response.status_code in const.STATUS_CODE_RANGE:
                time_response = time.time()
                time_link = time_response - time_request
                if stage == 2:
                    self.__request_obj_time.append([link, time_link])
                else:
                    self.__request_obj_time.append(time_link)
        except ConnectionError:
            pass

    # Thread sends request without proxy
    def request(self, link, stage):
        try:
            self.__headers = {"User-agent": random.choice(const.USER_AGENTS)}
            time.sleep(self.__create_delay())
            time_request = time.time()
            response = requests.get(link, headers=self.__headers)
            if response.status_code in const.STATUS_CODE_RANGE:
                time_response = time.time()
                time_link = time_response - time_request
                if stage == 2:
                    self.__request_obj_time.append([link, time_link])
                else:
                    self.__request_obj_time.append(time_link)
        except ConnectionError:
            pass

    def __create_delay(self):
        delay_time = random.uniform(0, 1)
        return delay_time

    """SECTION END"""
    """------------------------------------------------------------------------------------------------------"""

    """======================================================================================================"""
    """Creating payloads for SQL injection"""

    # https://example.com/page?attr1=value1&attr2=value2

    # Creates payloads by using index of the random value in the key:value pair
    def __payload_create(self, url, payload):
        index = self.__argument_indices_extractor(url)
        if index == -1:
            return f"{url[:-1]}{payload}"
        return f'{url[:index]}{payload}{url[index:]}'

    # Finds indices for value in the key:value pair
    def __argument_indices_extractor(self, url):
        index = random.choice(self.__get_and_list(url))
        return index

    # Get list of indices of & symbols in strings
    def __get_and_list(self, url):
        and_list = [i for i, ltr in enumerate(url) if ltr == "&"]
        and_list.append(-1)
        return and_list

    """SECTION END"""
    """------------------------------------------------------------------------------------------------------"""

    """======================================================================================================"""
    """Sending requests onto the website to get response times"""

    # Stage1: finding mean loading time of pages
    def __sql_check_stage1(self, link, use_proxy):
        thread_list = []
        times_sum = 0.0
        count = 0
        while count < const.NUM_MEAN:

            if use_proxy == "Y":
                thread = threading.Thread(target=self.request_proxy, daemon=True, args=(link, 1))
                thread.start()
                thread_list.append(thread)
            else:
                thread = threading.Thread(target=self.request, daemon=True, args=(link, 1))
                thread.start()
                thread_list.append(thread)

            count += 1

        for t in thread_list:
            t.join()

        # TODO: fix the issue that happens here
        print(self.__request_obj_time)
        for value in self.__request_obj_time:
            print(type(value))
            times_sum += value
        time_mean = times_sum / const.NUM_MEAN
        self.__request_obj_time.clear()
        return time_mean

    # Stage2: sending requests with payloads onto the website
    def __sql_check_stage2(self, link, time_mean, use_proxy):
        thread_list = []
        count = 0

        while True:
            try:
                payload_sql = next(self.__payload_gen)
                payload_link = self.__payload_create(link, payload_sql)

                if use_proxy == "Y":
                    thread = threading.Thread(target=self.request_proxy, daemon=True, args=(payload_link, 2))
                    thread.start()
                    thread_list.append(thread)
                else:
                    thread = threading.Thread(target=self.request, daemon=True, args=(payload_link, 2))
                    thread.start()
                    thread_list.append(thread)

            except StopIteration:
                for t in thread_list:
                    t.join()
                break

        while count < len(self.__request_obj_time):
            time_payload = self.__request_obj_time[count][1]
            payload_link = self.__request_obj_time[count][0]
            thread1 = threading.Thread(target=self.__vulnerability_check,
                                       args=(time_mean, time_payload, payload_link), daemon=True)
            thread1.start()
            count += 1
            thread1.join()

        return self.__stage2_results

    # SQLAnalysis main function
    def sql_check(self, use_proxy):
        proxy_obj = ProxyOperations()
        results = []
        for link in WebAnalysis.links_w_queries:
            if use_proxy == "Y":
                self.__proxy = proxy_obj.switch_proxy()
            time_mean = self.__sql_check_stage1(link, use_proxy)
            results = self.__sql_check_stage2(link, time_mean, use_proxy)
        return results

    """SECTION END"""
    """------------------------------------------------------------------------------------------------------"""

    """======================================================================================================"""
    """Detecting SQLi on the website"""

    # 0 - Client or Server Error
    # 1 - Not found
    # 2 - Low probability
    # 3 - Medium probability
    # 4 - High probability
    # 5 - SQL injection Found
    def __vulnerability_check(self, time_mean, time_payload, payload_link):
        if time_mean in range(0, 4):
            if time_payload < const.DELAY_TIME:
                # self.__stage2_results.append([1, time_payload, payload_link])
                pass
            else:
                self.__stage2_results.append([5, payload_link])

        else:
            if time_payload < const.NO_PROB * time_mean:
                # self.__stage2_results.append([1, time_payload, payload_link])
                pass
            elif time_payload > const.DELAY_TIME + const.VERY_HIGH_PROB * time_mean:
                self.__stage2_results.append([5, payload_link])

            elif time_payload > const.DELAY_TIME + const.HIGH_PROB * time_mean:
                self.__stage2_results.append([4, payload_link])

            elif time_payload > const.DELAY_TIME + const.MEDIUM_PROB * time_mean:
                self.__stage2_results.append([3, payload_link])

            elif time_payload > const.DELAY_TIME + const.LOW_PROB * time_mean:
                self.__stage2_results.append([2, payload_link])

            else:
                self.__stage2_results.append([1, payload_link])

    """SECTION END"""
    """------------------------------------------------------------------------------------------------------"""

    """======================================================================================================"""
    """======================================================================================================"""
    """======================================================================================================"""


def check_proxy(url):
    try:
        res = requests.get(url)
        if res.status_code not in range(200, 400):
            print(f"Error with {url}")
    except:
        print(f"Error with {url}")


if __name__ == "__main__":

    p = ProxyOperations()
    s = time.time()
    p.get_proxy_servers()
    f = time.time()
    print(f - s)

