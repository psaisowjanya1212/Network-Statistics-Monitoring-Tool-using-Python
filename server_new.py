import threading
import socket

MAXBUFLEN = 1024

def process_connection(sockfd,cli_addr):
    buffer = f"Received stats from {cli_addr}\n".encode()
    while True:
        try:
            buf = sockfd.recv(MAXBUFLEN)
            if buf:
                print(buffer)
                print(buf.decode().strip())
                print("\n")
        except Exception as e:
            print('Error:', e)
            break
    sockfd.close()

def main():
    port = 25108
    serv_sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv_sockfd.bind(('', port))
    serv_sockfd.listen(5)
    print('Server listening on port', port)

    while True:
        cli_sockfd, cli_addr = serv_sockfd.accept()
        print('Client connected from', cli_addr)

        t = threading.Thread(target=process_connection, args=(cli_sockfd, cli_addr))
        t.daemon = True
        t.start()

    serv_sockfd.close()

if __name__ == '__main__':
    main()

