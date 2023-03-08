import random
import threading
import requests
from bs4 import BeautifulSoup

import constants as const


"""========================================================================================================="""
"""========================================================================================================="""
"""========================================================================================================="""
"""All operations with proxy servers"""


class ProxyOperations:
    # Declaration of variables outside the constructor because they are not dependent on the object
    proxies_http = []
    proxies_https = []

    """======================================================================================================"""
    """PROXY SERVERS SETTERS AND GETTERS"""

    # Get proxy server lists through API and a website
    def get_proxy_servers(self):
        threads = []
        # Get proxies through API
        # response stores a proxy list
        response = requests.get(const.PROXY1)
        # Process of checking proxy servers whether they are working because this Server uses free proxies
        # and this is a common problem
        for url in response.text.splitlines():
            # Threading to speed up the process
            thread = threading.Thread(target=self.__check_http, args=(url,))
            thread.start()
            threads.append(thread)

        # Terminating threads
        for t in threads:
            t.join()
        threads.clear()

        # Get proxies from a website
        response = requests.get(const.PROXY2)
        # This time contents have to be extracted from the website manually
        soup = BeautifulSoup(response.text, 'html.parser')
        tr_elements = soup.find_all('tr')

        for row in tr_elements[1:]:
            # Finding all records in the list and extracting them
            td_elements = row.find_all('td')
            arguments = [td.text for td in td_elements]

            # Extracting only the useful parts from the list
            if len(arguments) == 8:
                url = f"http://{arguments[0]}:{arguments[1]}"
                # Checking whether proxy server is working
                if arguments[3] in const.COUNTRIES and arguments[6] == "yes":
                    # Starting threads that checks https proxy servers
                    thread = threading.Thread(target=self.__check_https, args=(url,))
                    thread.start()
                    threads.append(thread)

                elif arguments[3] in const.COUNTRIES and arguments[6] == "no":
                    # Starting threads that checks http proxy servers
                    thread = threading.Thread(target=self.__check_http, args=(url,))
                    thread.start()
                    threads.append(thread)

        # Stop all finished threads
        for t in threads:
            t.join()

    # Set a proxy server for requests library
    def switch_proxy(self):
        proxy = {}
        try:
            # Use random proxies
            proxy_http = random.choice(ProxyOperations.proxies_http)
            proxy["http"] = proxy_http
            proxy_https = random.choice(ProxyOperations.proxies_https)
            proxy["https"] = proxy_https

            return proxy
        # Sometimes list of https proxies is empty because there are none available(working ones)
        # Therefore sometimes you can use http proxy to access https website
        except IndexError:
            # Use same proxy both for http and https connections
            proxy["https"] = proxy["http"]
            return proxy

    """SECTION END"""
    """-----------------------------------------------------------------------------------------------------"""

    """======================================================================================================"""
    """Check whether proxy is working or not"""

    # Check status codes of http proxy servers and add them to http proxy list if they are working
    def __check_http(self, url):
        try:
            res = requests.get(url, timeout=7)
            if res.status_code in const.STATUS_CODE_RANGE:
                ProxyOperations.proxies_http.append(url)
        except:
            pass

    # Check status codes of https proxy servers and add them to https proxy list if they are working
    def __check_https(self, url):
        try:
            res = requests.get(url, timeout=7)
            if res.status_code in const.STATUS_CODE_RANGE:
                ProxyOperations.proxies_https.append(url)
        except:
            pass

    """SECTION END"""
    """-----------------------------------------------------------------------------------------------------"""


"""========================================================================================================="""
"""========================================================================================================="""
"""========================================================================================================="""
