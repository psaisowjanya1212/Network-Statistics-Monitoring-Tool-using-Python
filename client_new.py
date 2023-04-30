import socket
import time


PROC_NET_DEV = '/proc/net/dev'
UPDATE_INTERVAL = 1 # update interval in seconds
global interface_data_rates
interface_data_rates = {}

def get_interface_stats():
    with open(PROC_NET_DEV) as f:
        lines = f.readlines()
    stats = {}
    #i=0
    #global global_recv_data_rate = []
    for line in lines[2:]:
        parts = line.strip().split()
        iface_name = parts[0][:-1]
        recv_bytes = int(parts[1])
        recv_packets = int(parts[2])
        recv_errs = int(parts[3])
        recv_drop = int(parts[4])
        sent_bytes = int(parts[9])
        sent_packets = int(parts[10])
        sent_errs = int(parts[11])
        sent_drop = int(parts[12])
        stats[iface_name] = {
            'recv_packets': recv_packets,
            'recv_drop': recv_drop,
            'sent_packets': sent_packets,
            'sent_drop': sent_drop,
            'recv_bytes': recv_bytes,
            'sent_bytes': sent_bytes,
        }
        #global_recv_pkt_drops.append(recv_drop)
        
    return stats

def print_interface_stats(stats):
    message = ""
    for iface_name, iface_stats in stats.items():
        message += 'Interface: {}\n'.format(iface_name)
        message += 'Received: {} packets, {} dropped\n'.format(iface_stats["recv_packets"], iface_stats["recv_drop"])
        message += 'Sent: {} packets, {} dropped\n'.format(iface_stats["sent_packets"], iface_stats["sent_drop"])
    print(message)
    return message

def print_data_rate(stats_1, stats_2):
    message = ""
    global interface_data_rates
    for iface_name, iface_stats in stats_2.items():
        recv_bytes_1 = stats_1[iface_name]['recv_bytes']
        sent_bytes_1 = stats_1[iface_name]['sent_bytes']
        recv_bytes_2 = iface_stats['recv_bytes']
        sent_bytes_2 = iface_stats['sent_bytes']
        recv_rate = (recv_bytes_2 - recv_bytes_1) / (UPDATE_INTERVAL*1024*1024)
        sent_rate = (sent_bytes_2 - sent_bytes_1) / (UPDATE_INTERVAL*1024*1024)
        message += "Interface: {}\n".format(iface_name)
        message += "Received data rate: {:.3f} MB/s\n".format(recv_rate)
        message += "Sent data rate: {:.2f} MB/s\n".format(sent_rate)            
        interface_data_rates[iface_name] = {
        'recv_rate': recv_rate,
        'sent_rate': sent_rate,
        }
    print(message)
    return message

if __name__ == '__main__':
    # Define the server IP address and port
    SERVER_IP = '127.0.0.1'
    SERVER_PORT = 25108
    

    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    client_socket.connect((SERVER_IP, SERVER_PORT))
    while 1:
        stats_1 = get_interface_stats()
        time.sleep(UPDATE_INTERVAL)
        stats_2 = get_interface_stats()
        print_interface_stats(stats_2)
        message = "Recv or Send Data rate exceeded the threshold. Below are the additional details.\n"
        message += print_interface_stats(stats_2) # Include interface stats in message
        message += print_data_rate(stats_1, stats_2)
        # Send the message buffer to the server
        flag = False
        for iface_name, iface_stats in interface_data_rates.items():
            if iface_stats['recv_rate'] > 1 or iface_stats['sent_rate'] > 1:
                flag = True
                client_socket.sendall(message.encode())
                message = []
                break

    # Receive data from the server
    #data = client_socket.recv(1024)
    #print("Received from server: {data.decode()}')

    # Close the connection
    client_socket.close()

