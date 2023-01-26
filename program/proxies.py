import program.constants as const
import random
import program.web_analysis as web_object

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

    def __init__(self):
        self.proxies = []

        self.__options = Options()
        self.__options.add_argument("--headless")
        self.__options.add_argument("--window-size=1920x1080")
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
            self.proxies.append(elem)

        # Get proxies through webscraping
        self.driver.get(const.PROXY2)
        elements = self.driver.find_elements(By.TAG_NAME, "tr")
        for row in elements[1:]:
            arguments = row.text.split(" ")
            if len(arguments) == 10:
                if arguments[3] in const.COUNTRIES:
                    self.proxies.append(f"{arguments[0]}:{arguments[1]}")
            else:
                if f"{arguments[3]} {arguments[4]}" in const.COUNTRIES:
                    self.proxies.append(f"{arguments[0]}:{arguments[1]}")
        # self.driver.close()

    # Set a proxy program
    def switch_proxy_selenium(self):
        proxy = Proxy()
        proxy_ip_port = random.choice(self.proxies)
        proxy.proxy_type = ProxyType.MANUAL
        proxy.http_proxy = proxy_ip_port
        proxy.ssl_proxy = proxy_ip_port
        proxy.add_to_capabilities(self.__capabilities)
        web_object.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                                             options=self.__options, desired_capabilities=self.__capabilities)

    def switch_proxy_requests(self):
        proxy_ip_port = random.choice(self.proxies)
        proxy = {
            "http": proxy_ip_port,
            "https": proxy_ip_port
        }
        return proxy

    """SECTION END"""
    """------------------------------------------------------------------------------------------------------"""


"""========================================================================================================="""
"""========================================================================================================="""
"""========================================================================================================="""
