import requests
import random
import time
import threading

from web_analysis import WebAnalysis
from proxies import ProxyOperations
import constants as const


"""========================================================================================================="""
"""========================================================================================================="""
"""========================================================================================================="""
"""SQL Injection onto the website"""


class SQLAnalysis(WebAnalysis):
    def __init__(self):
        super().__init__()
        self.__payload_gen = (row for row in
                              open(const.sql_payload_wordlist, "r"))

        self.__proxy = {}
        self.__headers = {"User-agent": random.choice(const.USER_AGENTS)}
        self.__request_obj_time = []
        self.__stage2_results = []

    def request_proxy(self, link, stage):
        time_request = time.time()
        response = requests.get(link, proxies=self.__proxy, headers=self.__headers)
        if response.status_code in const.STATUS_CODE_RANGE:
            time_response = time.time()
            time_link = time_response - time_request
            if stage == 2:
                self.__request_obj_time.append([link, time_link])
            else:
                self.__request_obj_time.append(time_link)

    def request(self, link, stage):
        time_request = time.time()
        response = requests.get(link, headers=self.__headers)
        if response.status_code in const.STATUS_CODE_RANGE:
            time_response = time.time()
            time_link = time_response - time_request
            if stage == 2:
                self.__request_obj_time.append([link, time_link])
            else:
                self.__request_obj_time.append(time_link)

    """======================================================================================================"""
    """Database check for possible attack vectors"""

    def sql_check_stage1(self, link, use_proxy):
        thread_list = []
        times_sum = 0
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

        for value in self.__request_obj_time:
            times_sum += value
        time_mean = times_sum / const.NUM_MEAN
        self.__request_obj_time.clear()

        return time_mean

    def sql_check_stage2(self, link, time_mean, use_proxy):
        thread_list = []
        count = 0

        while True:
            try:
                payload_sql = next(self.__payload_gen)
                payload_link = self.payload_create(link, payload_sql)

                if use_proxy == "Y":
                    thread = threading.Thread(target=self.request_proxy, daemon=True, args=(payload_link, 2))
                    thread.start()
                    thread_list.append(thread)
                else:
                    thread = threading.Thread(target=self.request, daemon=True, args=(payload_link, 2))
                    thread.start()
                    thread_list.append(thread)

            except StopIteration:
                print("Payload list finished")
                for t in thread_list:
                    t.join()
                break

        while count < len(self.__request_obj_time):
            time_payload = self.__request_obj_time[count][1]
            payload_link = self.__request_obj_time[count][0]
            thread1 = threading.Thread(target=self.vulnerability_check,
                                       args=(time_mean, time_payload, payload_link), daemon=True)
            thread1.start()
            count += 1
            thread1.join()

        return self.__stage2_results

    # SQLAnalysis main function
    def sql_check(self, use_proxy):
        print("SERVER PT4")
        proxy_obj = ProxyOperations()
        results = []
        for link in self.links_w_queries:
            if use_proxy == "Y":
                self.__proxy = proxy_obj.switch_proxy_requests()
                print(self.__proxy)
            time_mean = self.sql_check_stage1(link, use_proxy)
            print("SERVER PT5")
            print(f"Time_mean: {time_mean}")
            results = self.sql_check_stage2(link, time_mean, use_proxy)
            print(results)
        return results




    """SECTION END"""
    """------------------------------------------------------------------------------------------------------"""

    """======================================================================================================"""
    """Sending requests and checking for errors in the status code"""

    # 0 - Client or Server Error
    # 1 - Not found
    # 2 - Low probability
    # 3 - Medium probability
    # 4 - High probability
    # 5 - SQL injection Found
    def vulnerability_check(self, time_mean, time_payload, payload_link):
        if time_mean in range(0, 4):
            if time_payload < const.DELAY_TIME:
                self.__stage2_results.append([1, time_payload, payload_link])

            else:
                self.__stage2_results.append([5, time_payload, payload_link])

        else:
            if time_payload < const.NO_PROB * time_mean:
                self.__stage2_results.append([1, time_payload, payload_link])

            elif time_payload > const.DELAY_TIME + const.VERY_HIGH_PROB * time_mean:
                self.__stage2_results.append([5, time_payload, payload_link])

            elif time_payload > const.DELAY_TIME + const.HIGH_PROB * time_mean:
                self.__stage2_results.append([4, time_payload, payload_link])

            elif time_payload > const.DELAY_TIME + const.MEDIUM_PROB * time_mean:
                self.__stage2_results.append([3, time_payload, payload_link])

            elif time_payload > const.DELAY_TIME + const.LOW_PROB * time_mean:
                self.__stage2_results.append([2, time_payload, payload_link])

            else:
                self.__stage2_results.append([1, time_payload, payload_link])

    """SECTION END"""
    """------------------------------------------------------------------------------------------------------"""

    """======================================================================================================"""
    """======================================================================================================"""
    """======================================================================================================"""
