from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class SQLAnalysis:

    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920x1080")
        # options.add_argument('--proxy-server=%s' % PROXY)
        # Sometimes needs to be updated by installing a new version into this folder
        self.driver = webdriver.Chrome("/usr/local/bin/chromedriver", options=options)
        file = open("payloads_query", "r")
        self.__payloads = file.read().split("\n")

        # TODO add driver.quit() at the end of the program to stop a driver from working
        # TODO check what happens to the driver and the system if requested .get multiple times
    def sql_query(self, url):
        page = self.driver.get(url)
        payloads = (i for i in self.__payloads)

        self.driver.close()
        self.driver.quit()

