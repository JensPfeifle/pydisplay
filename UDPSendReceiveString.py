import socket
import time
import httplib

BUFFER_SIZE = 1024
UDP_IP = '192.168.2.1'
UDP_PORT = 6000

RECEIVER_IP = '192.168.2.2'
RECEIVER_PORT = 8888

print('Creating UDP socket on {}:{}'.format(UDP_IP,UDP_PORT))
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create a UDP socket
sock.bind((UDP_IP, UDP_PORT))

def check_site_status(url, protocol='HTTPS'):
    """"
    Connects to a site, requests the header and returns the status.
    Returntype: tuple
    Returns: statuscode, status
    """
    print ("Checking {}".format(url))
    if protocol == 'HTTP':
        conn = httplib.HTTPSConnection(url,80)
    else:
        conn = httplib.HTTPSConnection(url,443)
    conn.request("HEAD", "/")
    r1 = conn.getresponse()
    return r1.status, r1.reason

if __name__ == '__main__':
    while True:
        data = ''
        for n in range(0,4):
            input_data = raw_input('Row{}:'.format(n))
            if len(input_data) < 20:
                data = data + '{:^20}'.format(input_data)
            else: print('Data too long for one row!')
        print ("Sending:{}".format(data))
        data_to_send = data
        sock.sendto(data_to_send, (RECEIVER_IP, RECEIVER_PORT))
        received_data, from_socket = sock.recvfrom(BUFFER_SIZE)
        print("Received: {} from {}".format(received_data,from_socket))
    sock.close()
