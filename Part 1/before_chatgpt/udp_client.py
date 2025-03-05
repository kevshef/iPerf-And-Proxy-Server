import socket
import datetime
import os

server_address = ("127.0.0.1", 4567)

def main():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            megabytes = int(input("Enter the amount of data to send in MB (enter -1 to exit):)").strip())

            if megabytes == -1:
                break

            message = os.urandom(megabytes * 1024 * 1024)
            
            print("Data sent (first 100 bytes):", message[:100])
            print("Time:", datetime.datetime.now())

            for i in range(0, len(message), 1024):
                chunk = message[i:i+1024]
                s.sendto(chunk, server_address)
    except Exception as e:
        print(e)
    finally:
        s.close()

if __name__ == "__main__":
    main()