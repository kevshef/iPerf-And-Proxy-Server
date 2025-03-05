import socket
import json

PROXY_IP = "127.0.0.1"
PROXY_PORT = 7001
BLOCKED_IPS = {"127.0.0.0", "10.0.0.5"}


def proxy(client_socket):
  data = client_socket.recv(1024).decode("utf-8")
  print(f"Data received from client: {data}")

  request = json.loads(data)
  message = request.get("message")

  if not message or len(message) != 4:
    response = json.dumps({"error": "Message must be 4 characters."})
    client_socket.send(response.encode("utf-8"))
    return

  server_ip = request.get("server_ip")
  server_port = request.get("server_port")


  if server_ip in BLOCKED_IPS:
    error = json.dumps({"message": "Error: Blocked IP"})
    client_socket.send(error.encode("utf-8"))
    client_socket.close()
    print("Error: Blocked IP")
    return


  proxy_request = {
    "proxy_ip": PROXY_IP,
    "proxy_port": PROXY_PORT,
    "message": message
  }
  json_data = json.dumps(proxy_request)

  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_socket.connect((server_ip, server_port))
  server_socket.send(json_data.encode("utf-8"))
  print(f"Sent to server: {json_data}")

  server_response = server_socket.recv(1024).decode("utf-8")
  print(f"Data received from server: {server_response}")

  client_socket.send(server_response.encode("utf-8"))
  print(f"Sent to client: {server_response}")
  server_socket.close()

  client_socket.close()


def start_proxy():
  proxy_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  proxy_server.bind((PROXY_IP, PROXY_PORT))
  proxy_server.listen(5)
  print(f"Proxy server listening on {PROXY_IP}:{PROXY_PORT}")

  for _ in range(10) :
    client_sock, _ = proxy_server.accept()
    proxy(client_sock)


if __name__ == "__main__":
  start_proxy()
