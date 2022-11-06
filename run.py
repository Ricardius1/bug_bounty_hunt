import socket

if __name__ == '__main__':
    # create connection between the server and the client
    ip = "127.0.0.1"
    port = 4444

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((ip, port))

    url = input("Give a url: ")

    if '"' in url or "'" in url:
        print("Invalid characters specified")
        exit()
    server.send(bytes(url, "utf-8"))
    server.close()

