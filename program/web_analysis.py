from bs4 import BeautifulSoup
import requests
import threading
import warnings

from urllib3.exceptions import InsecureRequestWarning

from proxies import ProxyOperations


"""========================================================================================================="""
"""========================================================================================================="""
"""========================================================================================================="""
"""DATA SEARCH, SORTING, PROXY, CRAWLING"""


class WebAnalysis:
    # Declaration of variables outside the constructor because they are not dependent on the object
    links = []
    links_w_queries = []

    # Constructor with input properties
    def __init__(self):
        self.__home_url = ""
        self.__domain = ""
        self.__proxy = {}
        self.proxy_object = ProxyOperations()
        # Statement to ignore all requests sent without verification
        warnings.simplefilter("ignore", InsecureRequestWarning)
    """======================================================================================================"""
    """SETTING THE USED DATA"""

    # Set the home url
    def set_home_url(self, home_url):
        self.__home_url = home_url
        WebAnalysis.links.append(self.__home_url)

    # Set the home url that has a query
    def set_query_url(self, home_url):
        self.__home_url = home_url
        WebAnalysis.links_w_queries.append(home_url)

    # Set home domain
    def set_domain(self):
        if self.__home_url[-1] != "/":
            self.__home_url += "/"
        slashes_list = [i for i, ltr in enumerate(self.__home_url) if ltr == "/"]
        self.__domain = self.__home_url[:slashes_list[2]]

    """SECTION END"""
    """------------------------------------------------------------------------------------------------------"""

    """======================================================================================================"""
    """FINDING URLS ON THE WEBSITE"""

    # Find URLs on the website
    def __find_links(self, link, use_proxy):
        try:
            if use_proxy == "Y":
                # Get request object of the web page
                page = requests.get(link, proxies=self.__proxy, verify=False)
            else:
                page = requests.get(link)
            soup = BeautifulSoup(page.content, "html.parser")

            # Extraction of all URLs from the page
            for link in soup.find_all("a"):
                href = link.get("href")
                # Checks whether there is a link, if it is not a local link, if it's on the same domain or subdomain
                if href is not None and "#" not in href:
                    # Concatenating domain to the url because some websites have relative URLs(/path/file)
                    if self.__domain not in href:
                        href = self.__domain + href
                    if href[-1] != "/":
                        href += "/"
                    # Looks for links with queries and adds them to according lists
                    if "?" in href:
                        WebAnalysis.links_w_queries.append(href)
                    else:
                        WebAnalysis.links.append(href)
        except requests.exceptions.ConnectionError:
            # TODO: check this part of the code
            pass

    # Checks if pages are from this domain
    def __check_domain(self, href):
        # Using .find() because if stops as soon as finds first occurrence
        index = href.find(self.__domain)
        if href[index-1] == "/" or href[index-1] == ".":
            return True
        return False

    """SECTION END"""
    """------------------------------------------------------------------------------------------------------"""

    """======================================================================================================"""
    """SORTING OF THE URLS AND GETTING QUERY KEYS"""

    # Removes duplicates from the links list
    def __sort_links(self):
        # Set and list for storing repeated links
        rep_path = set()
        rep_urls = []
        # Iterate over a list of links
        for index, link in enumerate(WebAnalysis.links):
            # Find and extract indices of slash signs in the list
            slashes_list = [i for i, ltr in enumerate(link) if ltr == "/"]
            num_slashes = len(slashes_list)
            # Checking only URLs that have more than 4 slashes because there the number of URLs with potential
            # queries is higher there. URLs that have 3 slashes are usually core pages that do not store many queries
            if num_slashes >= 4:
                url_path = link[slashes_list[2] + 1:slashes_list[-2]]
                if url_path in rep_path:
                    rep_urls.append(index)
                else:
                    rep_path.add(url_path)

        # Popping links from the links list from the end trying not to affect the order
        for i in reversed(rep_urls):
            WebAnalysis.links.pop(i)

    # Removes duplicates from the links_w_queries list
    # TODO: comment this method
    def __sort_links_w_queries(self):
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

    # Extracts query keys for the links with attributes
    def __get_query_keys(self):
        params = []
        for url in WebAnalysis.links_w_queries:
            # Splitting URL in 2 parts: URL and query part
            _, query = url.split("?")
            # Splitting example1=1&example2=2 into example1=1, example2=2
            fields = query.split("&")
            # TODO: finish explaining after this point
            inner_params = set()

            for field in fields:
                # Splitting example1=1 into example1, 1 and assigning for use only example1
                key, _ = field.split("=")
                inner_params.add(key)
            params.append(inner_params)
        return params

    """SECTION END"""
    """------------------------------------------------------------------------------------------------------"""

    """======================================================================================================"""
    """CRAWLING AND GETTING BUTTONS AND INPUT FIELDS """

    # Main function of WebAnalysis
    def web_crawler(self, level, use_proxy):
        thread_list = []
        start_num = 0
        stop_num = 1
        # Iterating deep in the website by the level the user has specified
        for i in range(level):
            # Webscraping links from all available URLs in links and links_w_queries
            all_links = (WebAnalysis.links + WebAnalysis.links_w_queries)
            # Option if user selected to use proxy
            if use_proxy == "Y":
                # Iterating over unchecked URLs
                for link in all_links[start_num:stop_num]:
                    # Switching proxy server for every request to avoid detection or prevention of blocked IP
                    self.__proxy = self.proxy_object.switch_proxy()
                    # Using threading module to speed up the process
                    thread = threading.Thread(target=self.__find_links, args=(link, use_proxy))
                    thread.start()
                    thread_list.append(thread)
            else:
                # Option if user selected not to use proxy
                for link in all_links[start_num:stop_num]:
                    # Using threading module to speed up the process
                    thread = threading.Thread(target=self.__find_links, args=(link, use_proxy))
                    thread.start()
                    thread_list.append(thread)

            # Terminating threads
            for t in thread_list:
                t.join()

            # Calling sorting functions to remove useless URLs
            self.__sort_links_w_queries()
            self.__sort_links()

            start_num = stop_num
            stop_num = len(self.links)

    """SECTION END"""
    """------------------------------------------------------------------------------------------------------"""

    """======================================================================================================"""
    """======================================================================================================"""
    """======================================================================================================"""
