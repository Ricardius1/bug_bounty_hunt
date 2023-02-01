import random
from proxies import ProxyOperations

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

"""========================================================================================================="""
"""========================================================================================================="""
"""========================================================================================================="""
"""DATA SEARCH, SORTING, PROXY, CRAWLING"""


class WebAnalysis:
    # TODO: remove WebAnalysis.links because they are not being used in the latest version of the program
    links = []
    links_w_queries = []

    # Constructor with input properties + initialisation of a web driver
    def __init__(self):
        self.__home_url = ""
        self.__domain = ""
        self.proxies = []
        self.proxy_object = ProxyOperations()

        # Assigning options to the webdriver
        self.__options = Options()
        self.__options.add_argument("--headless")
        self.__options.add_argument("--window-size=1920x1080")
        self.__options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36")
        self.__capabilities = webdriver.DesiredCapabilities.CHROME
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.__options,
                                       desired_capabilities=self.__capabilities)

    """======================================================================================================"""
    """SETTING THE USED DATA"""

    # Set the home url and the domain of the website
    def set_home_url(self, home_url):
        self.__home_url = home_url

        if self.__home_url[-1] != "/":
            self.__home_url += "/"
        WebAnalysis.links_w_queries.append(self.__home_url)
        slashes_list = [i for i, ltr in enumerate(self.__home_url) if ltr == "/"]
        self.__domain = self.__home_url[slashes_list[1] + 1:slashes_list[2]]

    def set_query_url(self, home_url):
        WebAnalysis.links_w_queries.append(home_url)
        print("SERVER PT2")

    """SECTION END"""
    """------------------------------------------------------------------------------------------------------"""

    """======================================================================================================"""
    """FINDING URLS ON THE WEBSITE"""

    def find_links(self, link):
        self.driver.get(link)
        # Looks for all link tags(<a>) on a page
        elements = self.driver.find_elements(By.TAG_NAME, 'a')
        for elem in elements:
            # Exports href attribute from a link tag
            href = elem.get_attribute('href')
            # Checks whether there is a link, if it is not a local link, if it's on the same domain or subdomain
            if href is not None and "#" not in href and self.__check_domain(href) is True:
                if href[-1] != "/":
                    href += "/"
                # Looks for links with attributes and adds them to the lists
                if "?" in href:
                    WebAnalysis.links_w_queries.append(href)
                else:
                    WebAnalysis.links.append(href)
        self.driver.close()

    # Checks if pages are from this domain
    def __check_domain(self, href):
        index = href.find(self.__domain)
        if href[index-1] == "/" or href[index-1] == ".":
            return True
        elif index == -1:
            return False
        return False

    """SECTION END"""
    """------------------------------------------------------------------------------------------------------"""

    """======================================================================================================"""
    """SORTING OF THE URLS AND GETTING QUERY KEYS"""

    # Delete duplicates in the links list
    def sort_links(self):
        # Set and list for storing repeated links
        rep_path = set()
        rep_urls = []
        # Iterate over a list of links
        for index, link in enumerate(WebAnalysis.links):
            # Find and extract indices of slashes in the list
            slashes_list = [i for i, ltr in enumerate(link) if ltr == "/"]
            num_slashes = len(slashes_list)
            if num_slashes >= 4:
                url_path = link[slashes_list[2] + 1:slashes_list[-2]]
                if url_path in rep_path:
                    rep_urls.append(index)
                else:
                    rep_path.add(url_path)

        # Popping links from the links list from the end
        for i in reversed(rep_urls):
            WebAnalysis.links.pop(i)

    def sort_links_w_queries(self):
        attr_list = self.__get_query_keys_iter()
        result = set()
        for index, attr in enumerate(attr_list[:-2]):
            curr_set_len = len(attr)
            for other_index, inner_attr in enumerate(attr_list[index:]):
                if other_index != 0:
                    inner_set_len = len(inner_attr)
                    repeated_attr = len(attr.intersection(inner_attr))
                    if repeated_attr == inner_set_len:
                        result.add(index + other_index)
                    elif repeated_attr == curr_set_len:
                        result.add(index)

        for i in reversed(list(result)):
            WebAnalysis.links_w_queries.pop(i)

    # TODO works twice faster than v1 but in case [{1,2}, {1,2,3}] leaves both elements present
    def sort_links_w_queries_v2(self):
        list_attr = self.__get_query_keys_iter()
        # list_attr = sorted(unsorted_list_attr, key=len)
        big_set = set()
        rep_urls = []
        # Iterate over a list of links
        for index, attr in enumerate(list_attr):
            curr_set_len = len(attr)
            # Check if current link queries already in the big_set and if True delete the link
            if len(attr.intersection(big_set)) == curr_set_len:
                rep_urls.append(index)
            else:
                for i in attr:
                    big_set.add(i)

        for i in reversed(list(rep_urls)):
            WebAnalysis.links_w_queries.pop(i)

    # Extracts query keys for the links with attributes
    def __get_query_keys_iter(self):
        params = []
        for url in WebAnalysis.links_w_queries:
            _, query = url.split("?")
            fields = query.split("&")
            inner_params = set()

            for field in fields:
                key, _ = field.split("=")
                inner_params.add(key)
            params.append(inner_params)
        return params

    # Extracts query keys from one input link
    def get_query_keys(self, url):
        params = []
        _, query = url.split("?")
        fields = query.split("&")
        inner_params = set()

        for field in fields:
            key, _ = field.split("=")
            inner_params.add(key)
        params.append(inner_params)
        return params

    def get_signs_list(self, url):
        sign_list = [i for i, ltr in enumerate(url) if ltr in ["=", "&", "?"]]
        return sign_list

    def get_and_list(self, url):
        and_list = [i for i, ltr in enumerate(url) if ltr == "&"]
        and_list.append(-1)
        return and_list

    """SECTION END"""
    """------------------------------------------------------------------------------------------------------"""

    """======================================================================================================"""
    """Creating payloads for different injections"""

    # https://example.com/page?attr1=value1&attr2=value2

    # Finds indices for value in the key:value pair
    def argument_indices_extractor(self, url):
        index = random.choice(self.get_and_list(url))
        return index

    # Creates payloads by using index of the random value in the key:value pair
    def payload_create(self, url, payload):
        index = self.argument_indices_extractor(url)
        if index == -1:
            return f"{url[:-1]}{payload}"
        return f'{url[:index]}{payload}{url[index:]}'

    """SECTION END"""
    """------------------------------------------------------------------------------------------------------"""

    """======================================================================================================"""
    """CRAWLING AND GETTING BUTTONS AND INPUT FIELDS """
    # Main function of WebAnalysis
    def web_crawler(self, level):
        self.links.append(self.__home_url)
        start_num = 0
        stop_num = 1
        self.proxy_object.get_proxy_servers()
        for i in range(level):
            # List of all urls
            all_links = (WebAnalysis.links + WebAnalysis.links_w_queries)
            for link in all_links[start_num:stop_num]:
                self.proxy_object.switch_proxy_selenium()
                self.find_links(link)
            self.sort_links_w_queries()
            self.sort_links()
            start_num = stop_num
            stop_num = len(self.links)

    # # Extract cookies from the page
    # def get_cookies(self):
    #     self.driver.get(self.__home_url)
    #     return self.driver.get_cookies()
    #
    # # TODO input and button
    # # Get input fields on the page
    # def get_input_fields(self, driver_object):
    #     input_list = []
    #     elements = driver_object.find_elements(By.TAG_NAME, "input")
    #     for elem in elements:
    #         input_list.append(elem)
    #     return input_list
    #
    # # Get button fields on the page
    # def get_button_fields(self, driver_object):
    #     button_list = []
    #     # TODO research how second parameter in the find_elements in selenium works(check if last 2 work)
    #
    #     #     self.driver.find_element(By.CSS_SELECTOR, "input[type = submit], button[type = submit]")
    #     html_buttons = ["input[type = 'submit']", "button[type = 'submit']", "input.submit", "button.submit"]
    #     elements = driver_object.find_elements(By.CSS_SELECTOR, html_buttons)
    #     for elem in elements:
    #         button_list.append(elem)
    #     return button_list

    """SECTION END"""
    """------------------------------------------------------------------------------------------------------"""

    """======================================================================================================"""
    """======================================================================================================"""
    """======================================================================================================"""



