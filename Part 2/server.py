import json
import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 7000
MESSAGE = "pong"

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(5)
print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

for _ in range(10):
	proxy_socket, addr = server_socket.accept()
	data = proxy_socket.recv(1024).decode("utf-8")


	request = json.loads(data)

	addr_info = request.get("proxy_ip")
	message_received = request.get("message")


	response = json.dumps({
		"message": MESSAGE,
	})

	print(f"Received : {message_received}")

	proxy_socket.send(response.encode("utf-8"))

	print(f"Data sent : {response}")

	proxy_socket.close()