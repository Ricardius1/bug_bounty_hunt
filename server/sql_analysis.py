import requests
from web_analysis import WebAnalysis
from proxies import ProxyOperations
import constants as const
import time


"""========================================================================================================="""
"""========================================================================================================="""
"""========================================================================================================="""
"""SQL Injection onto the website"""


class SQLAnalysis(WebAnalysis):
    # TODO maybe add blind sql method
    def __init__(self):
        super().__init__()
        self.payload_gen = (row for row in
                            open("server/wordlists/sql_payloads/Intruder/detect/Generic_TimeBased.txt", "r"))
        self.proxy = {}

    """======================================================================================================"""
    """Database check for possible attack vectors"""

    def sql_check_stage1(self, link):
        times_sum = 0
        count = 0
        while count < const.num_mean:
            time_request = time.time()
            requests.get(link, proxies=self.proxy)
            time_response = time.time()
            times_sum += time_response-time_request
            count += 1
        time_mean = times_sum / const.num_mean
        return time_mean

    def sql_check_stage2(self, link, time_mean):
        list_results = []
        while True:
            payload_sql = next(self.payload_gen)
            if payload_sql != "":
                payload_link = self.payload_create(link, payload_sql)
                time_request = time.time()
                response = requests.get(payload_link, proxies=self.proxy)
                time_response = time.time()
                if response.status_code in const.status_code_range:
                    time_payload = time_response - time_request
                    list_results.append(self.vulnerability_check(time_mean, time_payload))

                else:
                    list_results.append(0)
            else:
                return list_results

    def sql_analysis(self):
        proxy_obj = ProxyOperations()
        results = []
        for link in self.links_w_queries:
            self.proxy = proxy_obj.switch_proxy_requests()
            time_mean = self.sql_check_stage1(link)
            results = self.sql_check_stage2(link, time_mean)
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
    def vulnerability_check(self, time_mean, time_payload):
        if time_mean in range(0, 4):
            if time_payload < const.delay_time:
                return 1
            else:
                return 5

        else:
            if time_payload < const.no_prob * time_mean:
                return 1
            elif time_payload > const.delay_time + const.very_high_prob * time_mean:
                return 5
            elif time_payload > const.delay_time + const.high_prob * time_mean:
                return 4
            elif time_payload > const.delay_time + const.medium_prob * time_mean:
                return 3
            elif time_payload > const.delay_time + const.low_prob * time_mean:
                return 2
            else:
                return 1

    """SECTION END"""
    """------------------------------------------------------------------------------------------------------"""

    """======================================================================================================"""
    """======================================================================================================"""
    """======================================================================================================"""
