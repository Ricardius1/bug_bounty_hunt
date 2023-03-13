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
        # Assigning generator that stores wordlist
        self.__payload_gen = (row.rstrip() for row in
                              open(const.SQL_PAYLOAD_WORDLIST, "r"))
        # Function that ignores a warning caused by putting verify=False in request.get()
        warnings.simplefilter("ignore", InsecureRequestWarning)
        # Class attributes
        self.__proxy = {}
        self.__headers = {}
        self.__request_obj_time = []
        self.__stage2_results = []

    """======================================================================================================"""
    """Creating and checking request objects"""

    # Thread sends request with proxy
    def request_proxy(self, link, stage):
        try:
            # Randomly selecting headers to minimise chance of being blocked by the web server
            self.__headers = {"User-agent": random.choice(const.USER_AGENTS)}
            # Randomly creating short delay(0-1s) to minimise chance of being blocked by the web server
            time.sleep(self.__create_delay())
            # Start measuring time
            time_request = time.time()
            # Send GET request
            response = requests.get(link, proxies=self.__proxy, headers=self.__headers, verify=False)
            # Checking if request was successful
            if response.status_code in const.STATUS_CODE_RANGE:
                # Finish time
                time_response = time.time()
                # Time to receive a page back
                time_link = time_response - time_request
                # Depending on stage of scan different outputs
                if stage == 2:
                    self.__request_obj_time.append([link, time_link])
                else:
                    self.__request_obj_time.append(time_link)
        # If there is any problems with a website or proxy there will be connection error
        except ConnectionError:
            pass

    # Thread sends request without proxy
    # This is alomst exact copy of request_proxy method but request here is sent without help of proxy
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

    # Randomly create delay for (0,1) seconds before sending a new request
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
        # Method that decides where to place payload in the link
        index = self.__argument_indices_extractor(url)
        # Different code is needed to place payload in the last part
        if index == -1:
            return f"{url[:-1]}{payload}"
        return f'{url[:index]}{payload}{url[index:]}'

    # Finds indices for value in the key:value pair
    def __argument_indices_extractor(self, url):
        # Randomly select index of the place where to place the payload in the URL
        index = random.choice(self.__get_and_list(url))
        return index

    # Get list of indices of & symbols in strings
    def __get_and_list(self, url):
        # Extract all the indices where AND sign was found as the placement of payload has to be one index before it
        and_list = [i for i, ltr in enumerate(url) if ltr == "&"]
        # Last index can also be place to put the payload
        and_list.append(-1)
        return and_list

    """SECTION END"""
    """------------------------------------------------------------------------------------------------------"""

    """======================================================================================================"""
    """Sending requests onto the website to get response times"""

    # Stage1: finding mean loading time of pages
    def __sql_check_stage1(self, link, use_proxy):
        thread_list = []
        count = 0
        # Sending requests to the page NUM_MEAN amount of times to reassure that the mean is accurate
        while count < const.NUM_MEAN:
            # Either sending requests with proxy or not
            if use_proxy == "Y":
                # Set a target function and pass arguments
                thread = threading.Thread(target=self.request_proxy, daemon=True, args=(link, 1))
                # Start a thread
                thread.start()
                # Append thread object to the list
                thread_list.append(thread)
            else:
                # This function does exactly the same operation as function above just without proxy
                thread = threading.Thread(target=self.request, daemon=True, args=(link, 1))
                thread.start()
                thread_list.append(thread)

            count += 1

        # Stopping point for all additional threads that were created in this method
        for t in thread_list:
            t.join()

        # Calculating mean response time
        print(self.__request_obj_time)
        times_sum = sum(self.__request_obj_time)
        time_mean = times_sum / const.NUM_MEAN
        self.__request_obj_time.clear()
        return time_mean

    # Stage2: sending requests with payloads onto the website
    def __sql_check_stage2(self, link, time_mean, use_proxy):
        thread_list = []
        count = 0

        # Sending payloads to the website
        while True:
            try:
                # Using generator to save memory space and get a payload
                payload_sql = next(self.__payload_gen)
                # Creating a URL with payload
                payload_link = self.__payload_create(link, payload_sql)

                # Using threads to send requests to the server with payloads in the URLs
                # This time because it is stage 2 __request_obj_time will store different data type
                if use_proxy == "Y":
                    thread = threading.Thread(target=self.request_proxy, daemon=True, args=(payload_link, 2))
                    thread.start()
                    thread_list.append(thread)
                else:
                    thread = threading.Thread(target=self.request, daemon=True, args=(payload_link, 2))
                    thread.start()
                    thread_list.append(thread)

            # This is the break case of while loop
            except StopIteration:
                # Terminate execution of all used threads in this method
                for t in thread_list:
                    t.join()
                break

        # Analysing whether the injection was successful or not
        # Request_obj_time now is a 2d array with [payload_link, time_payload] inside
        while count < len(self.__request_obj_time):
            # Assigning variables
            time_payload = self.__request_obj_time[count][1]
            payload_link = self.__request_obj_time[count][0]
            # Creating threads to check for vulnerabilities faster
            thread1 = threading.Thread(target=self.__vulnerability_check,
                                       args=(time_mean, time_payload, payload_link), daemon=True)
            thread1.start()
            count += 1
            thread1.join()

        return self.__stage2_results

    # SQLAnalysis main function
    def sql_check(self, use_proxy):
        # Instantiate proxy object
        proxy_obj = ProxyOperations()
        results = []
        # Check every link remaining in the links_w_queries list after the sort
        for link in WebAnalysis.links_w_queries:
            if use_proxy == "Y":
                self.__proxy = proxy_obj.switch_proxy()
            # Find mean time of a link that is being checked right now
            time_mean = self.__sql_check_stage1(link, use_proxy)
            #
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

    # Method that checks whether SQL vulnerability is present or not
    # It does it by analyzing the change in time between the mean + delay time in the payload to the payload time
    # This way we can see if the change is significant enough to prove that there is SQL injection on the website
    def __vulnerability_check(self, time_mean, time_payload, payload_link):
        # If the mean response time is in the normal range then there is no need for coefficients
        if time_mean in range(0, 4):
            # I decided not to add no SQL found result to the output because there is no need, but it could be done just
            # by uncommenting line below
            if time_payload < const.DELAY_TIME:
                # self.__stage2_results.append([1, time_payload, payload_link])
                pass
            else:
                self.__stage2_results.append([5, payload_link])

        # But if mean response time is greater than 4 seconds then it is outside the  normal range, so to check
        # precisely coefficients have to be used
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
