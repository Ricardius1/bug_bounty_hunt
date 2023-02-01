import constants as const
import random
import web_analysis as web_object

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

"""========================================================================================================="""
"""========================================================================================================="""
"""========================================================================================================="""
"""All operations with proxy servers"""


class ProxyOperations:
    proxies_http = []
    proxies_https = []

    def __init__(self):

        self.__options = Options()
        self.__options.add_argument("--headless")
        self.__options.add_argument("--window-size=1920x1080")
        self.__options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36")
        self.__capabilities = webdriver.DesiredCapabilities.CHROME
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.__options,
                                       desired_capabilities=self.__capabilities)

    """======================================================================================================"""
    """PROXY SERVERS SETTERS AND GETTERS"""

    # Get proxy list through API
    def get_proxy_servers(self):
        # Get proxies through API
        self.driver.get(const.PROXY1)
        elements = self.driver.find_element(By.TAG_NAME, "pre").text
        for elem in elements.splitlines():
            ProxyOperations.proxies_http.append(f"http://{elem}")

        # Get proxies through webscraping
        self.driver.get(const.PROXY2)
        elements = self.driver.find_elements(By.TAG_NAME, "tr")
        for row in elements[1:]:
            arguments = row.text.split(" ")
            if len(arguments) == 10:
                if arguments[3] in const.COUNTRIES and arguments[6] == "yes":
                    ProxyOperations.proxies_https.append(f"http://{arguments[0]}:{arguments[1]}")
            else:
                if f"{arguments[3]} {arguments[4]}" in const.COUNTRIES and arguments[6] == "yes":
                    ProxyOperations.proxies_https.append(f"http://{arguments[0]}:{arguments[1]}")
        print("SERVER PT3")
        print(ProxyOperations.proxies_https)
        self.driver.close()

    # Set a proxy program
    def switch_proxy_selenium(self):
        proxy = Proxy()
        proxy_http = random.choice(ProxyOperations.proxies_http)
        proxy_https = random.choice(ProxyOperations.proxies_https)
        proxy.proxy_type = ProxyType.MANUAL
        proxy.http_proxy = proxy_http
        proxy.ssl_proxy = proxy_https
        proxy.add_to_capabilities(self.__capabilities)
        web_object.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                                             options=self.__options, desired_capabilities=self.__capabilities)

    def switch_proxy_requests(self):
        proxy_http = random.choice(ProxyOperations.proxies_http)
        proxy_https = random.choice(ProxyOperations.proxies_https)
        proxy = {
            "http": proxy_http,
            "https": proxy_https
                }
        return proxy

    """SECTION END"""
    """------------------------------------------------------------------------------------------------------"""


"""========================================================================================================="""
"""========================================================================================================="""
"""========================================================================================================="""
