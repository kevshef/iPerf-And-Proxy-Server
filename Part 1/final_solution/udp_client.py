import socket
import datetime
import os
import struct
import math
import time

# Client configuration
SERVER_ADDRESS = ("127.0.0.1", 4567)
PACKET_SIZE = 1024           # total packet size (including header)
PACKET_HEADER_SIZE = 4       # 4 bytes for sequence number
DATA_SIZE = PACKET_SIZE - PACKET_HEADER_SIZE
WINDOW_SIZE = 10             # maximum unacknowledged packets in flight
TIMEOUT_INTERVAL = 0.5       # retransmission timeout (seconds)

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        while True:
            user_input = input("Enter the amount of data to send in MB (enter -1 to exit): ").strip()
            try:
                megabytes = int(user_input)
            except ValueError:
                print("Please enter a valid integer.")
                continue

            if megabytes == -1:
                break

            # Generate payload.
            payload = os.urandom(megabytes * 1024 * 1024)
            payload_size = len(payload)
            total_packets = math.ceil(payload_size / DATA_SIZE)
            send_timestamp = datetime.datetime.now()

            # Send header with payload size.
            header = f"SIZE:{payload_size}".encode()
            client_socket.sendto(header, SERVER_ADDRESS)

            # Print transmission details.
            print("\n--- Client Transmission Details ---")
            print(f"Client IP: {client_socket.getsockname()[0]} | Server IP: {SERVER_ADDRESS[0]}")
            print(f"Data size: {payload_size} bytes ({megabytes} MB)")
            print("Data sent (first 100 bytes):", payload[:100])
            print("Timestamp of sending:", send_timestamp)
            print(f"Total packets to send: {total_packets}")
            print("-----------------------------------\n")

            # Prepare packets with a 4-byte sequence number header.
            packets = []
            for seq in range(total_packets):
                start_idx = seq * DATA_SIZE
                end_idx = min((seq + 1) * DATA_SIZE, payload_size)
                packet = struct.pack('!I', seq) + payload[start_idx:end_idx]
                packets.append(packet)
            
            # Sliding window protocol variables.
            base = 0
            next_seq = 0
            unacked = {}  # maps sequence number -> (packet, time_sent)
            
            client_socket.setblocking(0)  # switch to non-blocking mode
            
            # Send packets and handle retransmissions.
            while base < total_packets:
                # Send new packets if window is not full.
                while next_seq < total_packets and next_seq < base + WINDOW_SIZE:
                    client_socket.sendto(packets[next_seq], SERVER_ADDRESS)
                    unacked[next_seq] = (packets[next_seq], time.time())
                    next_seq += 1
                
                # Try to receive ACKs.
                try:
                    ack_data, _ = client_socket.recvfrom(1024)
                    if len(ack_data) >= 4:
                        ack_seq = struct.unpack('!I', ack_data[:4])[0]
                        if ack_seq in unacked:
                            del unacked[ack_seq]
                            # Slide the window: advance 'base' if the next expected seq is acknowledged.
                            while base not in unacked and base < next_seq:
                                base += 1
                except BlockingIOError:
                    # No ACK received at the moment.
                    pass
                
                # Check for packet timeouts and retransmit if needed.
                current_time = time.time()
                for seq, (pkt, sent_time) in list(unacked.items()):
                    if current_time - sent_time > TIMEOUT_INTERVAL:
                        client_socket.sendto(pkt, SERVER_ADDRESS)
                        unacked[seq] = (pkt, current_time)
                
                time.sleep(0.01)  # small delay to prevent busy looping

            print("All packets acknowledged.")
            
            # Wait for throughput message from server.
            client_socket.settimeout(10)
            try:
                response, addr = client_socket.recvfrom(1024)
                throughput_value = response.decode()
                print(f"Throughput reported by server: {throughput_value} KB/s\n")
            except socket.timeout:
                print("No throughput response from server. Transmission might have failed.\n")
                
    except Exception as e:
        print("An error occurred:", e)
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
