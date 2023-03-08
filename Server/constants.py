"""proxies.py"""

COUNTRIES = {"United States", "Germany", "United Kingdom", "France", "Italy", "Spain", "Ukraine", "Poland",
             "Romania", "Netherlands", "Belgium", "Czech Republic", "Greece", "Portugal", "Sweden",
             "Hungary", "Austria", "Switzerland", "Bulgaria", "Denmark", "Finland", "Slovakia", "Norway",
             "Ireland", "Croatia", "Moldova", "Lithuania", "Slovenia", "Latvia", "Estonia", "Iceland"}

PROXY1 = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=DE,GB,AL,AD,AM,AT,BY,BE,BA,BG,CH,CY,CZ,DE,DK,ES,FR,GR,HU,HR,IE,IS,IT,LU,NO,NL,PT&ssl=all&anonymity=all"
PROXY2 = "https://free-proxy-list.net"


"""sql_analysis.py"""

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
]

SQL_PAYLOAD_WORDLIST = "../Server/wordlists/Generic_TimeBased.txt"

STATUS_CODE_RANGE = range(200, 400)
NUM_MEAN = 5
DELAY_TIME = 5
NO_PROB = 1.4
VERY_HIGH_PROB = 0.95
HIGH_PROB = 0.85
MEDIUM_PROB = 0.7
LOW_PROB = 0.5
