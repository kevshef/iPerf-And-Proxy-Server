import socket
import json

PROXY_IP = "127.0.0.1"
PROXY_PORT = 7001
MESSAGE = "ping"

SERVER_IP = "127.0.0.1"
SERVER_PORT = 7000


data = json.dumps({
	"server_ip": SERVER_IP,
	"server_port": SERVER_PORT,
	"message": MESSAGE
})

for _ in range(10):
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect((PROXY_IP, PROXY_PORT))


	client_socket.send(data.encode("utf-8"))
	print(f"Data sent: {data}")

	response = client_socket.recv(1024).decode("utf-8")

	to_json = json.loads(response)
	message = to_json.get("message")

	print(f"Response received: {message}")

	client_socket.close()
