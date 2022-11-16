from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# File with functions relating to getting data from a page


class WebAnalysis:
    links = []
    links_w_queries = []
    cookies = []
    fields_input = []

    # Constructor with input properties + initialisation of a web driver
    def __init__(self, home_url):
        self.__home_url = home_url
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920x1080")
        # options.add_argument('--proxy-server=%s' % PROXY)
        # Sometimes needs to be updated by installing a new version into this folder
        self.driver = webdriver.Chrome("/usr/local/bin/chromedriver", options=options)
        # Get the domain of the website
        if self.__home_url[-1] != "/":
            self.__home_url += "/"
        WebAnalysis.links.append(self.__home_url)
        slashes_list = [i for i, ltr in enumerate(self.__home_url) if ltr == "/"]
        self.__domain = self.__home_url[slashes_list[1] + 1:slashes_list[2]]

    # Checks if pages are from this domain
    def __check_domain(self, href):
        index = href.find(self.__domain)
        if href[index-1] == "/" or href[index-1] == ".":
            return True
        elif index == -1:
            return False
        return False

    # Extracts query keys for the links with attributes
    def __get_query_keys(self):
        params = []
        for link in WebAnalysis.links_w_queries:
            _, query = link.split("?")
            fields = query.split("&")
            inner_params = set()

            for field in fields:
                key, _ = field.split("=")
                inner_params.add(key)
            params.append(inner_params)
        return params

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

    # TODO change sorting to take into account the rest of the url and not just query
    def sort_links_w_queries(self):
        attr_list = self.__get_query_keys()
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
        list_attr = self.__get_query_keys()
        # list_attr = sorted(unsorted_list_attr, key=len)
        big_set = set()
        rep_urls = []
        # Iterate over a list of links
        for index, attr in enumerate(list_attr):
            curr_set_len = len(attr)
            # Check if current link queries already in the big_set and if True delete the link
            # if big_set.difference(attr) != set():
            if len(attr.intersection(big_set)) == curr_set_len:
                rep_urls.append(index)
            else:
                for i in attr:
                    big_set.add(i)

        for i in reversed(list(rep_urls)):
            WebAnalysis.links_w_queries.pop(i)

    # Looks for links on the html page and sorts them
    # TODO decide if we need to add links_w_attr in links
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

    # Extract cookies from the page
    def get_cookies(self):
        self.driver.get(self.__home_url)
        return self.driver.get_cookies()

    # Get proxy list API
    def get_proxy_list(self):
        proxy_list = []
        driver = self.driver
        driver.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all")
        elements = driver.find_element(By.TAG_NAME, "pre").text
        for elem in elements.splitlines():
            proxy_list.append(elem)
        return proxy_list

    # TODO input and button
    # Get input fields on the page
    def get_input_fields(self, driver_object):
        input_list = []
        elements = driver_object.find_elements(By.TAG_NAME, "input")
        for elem in elements:
            input_list.append(elem)
        return input_list
        # for link in self.links:
        #     self.driver.get(link)
        #     elem = self.driver.find_element(By.TAG_NAME, "input")
        #     return elem

    # Get button fields on the page
    def get_button_fields(self, driver_object):
        button_list = []
        # TODO research how second parameter in the find_elements in selenium works(check if last 2 work)

        #     self.driver.find_element(By.CSS_SELECTOR, "input[type = submit], button[type = submit]")
        html_buttons = ["input[type = 'submit']", "button[type = 'submit']", "input.submit", "button.submit"]
        elements = driver_object.find_elements(By.CSS_SELECTOR, html_buttons)
        for elem in elements:
            button_list.append(elem)
        return button_list

    # TODO add sorting, using proxy, level input
    # Main function of WebAnalysis
    def web_crawler(self):
        self.links.append(self.__home_url)
        start_num = 0
        stop_num = 1
        for i in range(3):
            for link in self.links[start_num:stop_num]:
                self.find_links(link)
            self.sort_links_w_queries()
            self.sort_links()
            start_num = stop_num
            stop_num = len(self.links)


    def add_new_stuff(self):
        pass