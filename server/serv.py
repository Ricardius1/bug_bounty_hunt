import socket
from server.web_analysis import WebAnalysis


if __name__ == '__main__':
    #
    #
    # Client-server connection block start
    #
    #
    ip = "127.0.0.1"
    port = 4444

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen(20)

    while True:
        client, address = server.accept()
        print(f"Connection established - {address[0]}:{address[1]}")

        start_url = client.recv(1024)
        start_url = start_url.decode("utf-8")
        client.close()
        if '"' in start_url or "'" in start_url:
            print("Invalid characters specified")
            exit()
    #
    #
    # Client-server connection block stop
    #
    #
    #
    #
    # WebAnalysis start
    #
    #
        s = WebAnalysis(start_url)
        # Number of searches of links
        for i in range(3):
            pass


        # start_num = 0
        # stop_num = 1
        # for i in range(3):
        #     for link in self.links[start_num:stop_num]:
        #         self.find_links(link)
        #     self.sort_links_w_queries()
        #     self.sort_links()
        #     start_num = stop_num
        #     stop_num = len(self.links)



