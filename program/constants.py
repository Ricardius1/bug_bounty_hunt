import socket

"""proxies.py"""

COUNTRIES = {"United States", "Germany", "United Kingdom", "France", "Italy", "Spain", "Ukraine", "Poland",
             "Romania", "Netherlands", "Belgium", "Czech Republic", "Greece", "Portugal", "Sweden",
             "Hungary", "Austria", "Switzerland", "Bulgaria", "Denmark", "Finland", "Slovakia", "Norway",
             "Ireland", "Croatia", "Moldova", "Lithuania", "Slovenia", "Latvia", "Estonia", "Iceland"}

PROXY1 = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
PROXY2 = "https://free-proxy-list.net"


"""sql_analysis.py"""

STATUS_CODE_RANGE = range(200, 400)
NUM_MEAN = 3
DELAY_TIME = 5
NO_PROB = 1.4
VERY_HIGH_PROB = 0.95
HIGH_PROB = 0.85
MEDIUM_PROB = 0.7
LOW_PROB = 0.5

"""server.py"""

SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 5050
ADDR = (SERVER_IP, SERVER_PORT)
HEADER = 64
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!exit"

"""extra_functions.py"""

font_black = "30"
font_red = "31"
font_green = "32"
font_yellow = "33"
font_blue = "34"
font_magenta = "35"
font_cyan = "36"
font_white = "37"
font_default = "39"

# If you want to add background take 40 - black 41 - red
