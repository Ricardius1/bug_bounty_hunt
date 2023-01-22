COUNTRIES = {"United States", "Germany", "United Kingdom", "France", "Italy", "Spain", "Ukraine", "Poland",
             "Romania", "Netherlands", "Belgium", "Czech Republic", "Greece", "Portugal", "Sweden",
             "Hungary", "Austria", "Switzerland", "Bulgaria", "Denmark", "Finland", "Slovakia", "Norway",
             "Ireland", "Croatia", "Moldova", "Lithuania", "Slovenia", "Latvia", "Estonia", "Iceland"}

proxy1 = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
proxy2 = "https://free-proxy-list.net"


status_code_range = range(200, 400)
# Has to be greater than 1
num_mean = 3
delay_time = 5
no_prob = 1.4
very_high_prob = 0.95
high_prob = 0.85
medium_prob = 0.7
low_prob = 0.5
