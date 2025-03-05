import socket
import signal
import sys

server_ip = "127.0.0.1"
server_port = 4567
buffer_size = 65535
data = bytearray()
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def main():
    try:
        s.bind((server_ip, server_port))
        s.settimeout(1)
        while True:
            try:
                msg, addr = s.recvfrom(buffer_size)
                data.extend(msg)
                print(data)
            except socket.timeout:
                continue
    except Exception as e:
        print(e)
    finally:
        s.close()

def handler(signal_received, frame):
    print("SIGINT or CTRL-C detected. Exiting gracefully")
    s.close()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    main()