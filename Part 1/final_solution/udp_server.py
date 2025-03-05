import socket
import signal
import sys
import datetime
import struct
import math

# Server configuration
SERVER_IP = "127.0.0.1"
SERVER_PORT = 4567
BUFFER_SIZE = 65535
TIMEOUT = 5  # seconds

# Protocol constants
HEADER_PREFIX = b"SIZE:"  # header for payload size
PACKET_HEADER_SIZE = 4    # 4 bytes for sequence number
PACKET_SIZE = 1024        # total packet size (including header)
DATA_SIZE = PACKET_SIZE - PACKET_HEADER_SIZE  # usable data per packet

# Create and bind the UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.settimeout(TIMEOUT)
print(f"Server started at {SERVER_IP}:{SERVER_PORT}")

def graceful_shutdown(signal_received, frame):
    print("SIGINT or CTRL-C detected. Exiting gracefully.")
    server_socket.close()
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)

while True:
    print("\nWaiting for new transmission...")
    data_packets = {}    # mapping: sequence number -> data bytes
    total_payload_size = None
    total_packets = None
    client_address = None
    start_time = None

    # Wait for header containing the payload size.
    while total_payload_size is None:
        try:
            packet, addr = server_socket.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            continue
        if packet.startswith(HEADER_PREFIX):
            try:
                total_payload_size = int(packet.decode()[len("SIZE:"):])
            except ValueError:
                print("Invalid size header received.")
                continue
            client_address = addr
            total_packets = math.ceil(total_payload_size / DATA_SIZE)
            print(f"Header received from {addr[0]}:{addr[1]}")
            print(f"Expected payload size: {total_payload_size} bytes in {total_packets} packets")
            start_time = datetime.datetime.now()
            print("Started receiving data at:", start_time)
        else:
            print("Received non-header packet while waiting for header.")

    # Receive data packets until all packets are collected.
    while len(data_packets) < total_packets:
        try:
            packet, addr = server_socket.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            print("Timeout while waiting for packets.")
            break
        if len(packet) < PACKET_HEADER_SIZE:
            continue
        seq_num = struct.unpack('!I', packet[:PACKET_HEADER_SIZE])[0]
        payload_data = packet[PACKET_HEADER_SIZE:]
        # Avoid storing duplicates.
        if seq_num not in data_packets:
            data_packets[seq_num] = payload_data
        # Send ACK back for this packet (4-byte sequence number).
        ack_packet = struct.pack('!I', seq_num)
        try:
            server_socket.sendto(ack_packet, addr)
        except Exception as e:
            print("Error sending ACK:", e)

    end_time = datetime.datetime.now()
    if len(data_packets) < total_packets:
        print("Incomplete data received.")
        if client_address:
            try:
                error_message = "ERROR: Incomplete data received"
                server_socket.sendto(error_message.encode(), client_address)
            except Exception as e:
                print("Error sending error message to client:", e)
    else:
        # Reassemble payload in order.
        payload_data = bytearray()
        for seq in range(total_packets):
            payload_data.extend(data_packets.get(seq, b""))
        duration = (end_time - start_time).total_seconds()
        throughput_bps = total_payload_size / duration if duration > 0 else 0
        throughput_kbps = throughput_bps / 1024

        print("Finished receiving data at:", end_time)
        print("\n--- Transmission Details ---")
        print(f"Server IP: {SERVER_IP} | Client IP: {client_address[0]}")
        print(f"Total data received: {total_payload_size} bytes")
        print(f"Received data (first 100 bytes): {payload_data[:100]}")
        print(f"Reception started at: {start_time}")
        print(f"Reception ended at  : {end_time}")
        print(f"Computed Throughput: {throughput_kbps:.2f} KB/s")
        print("-----------------------------\n")

        # Send throughput back to the client.
        try:
            throughput_message = f"{throughput_kbps:.2f}"
            server_socket.sendto(throughput_message.encode(), client_address)
        except Exception as e:
            print("Error sending throughput to client:", e)
