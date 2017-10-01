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
    Returns a tuple of strings: statuscode, status
    """
    print ("Checking {}".format(url))
    if protocol == 'HTTP':
        conn = httplib.HTTPSConnection(url,80)
    else:
        conn = httplib.HTTPSConnection(url,443)
    conn.request("HEAD", "/")
    r1 = conn.getresponse()
    return r1.status, r1.reason

def make_data_to_send(row0, row1, row2, row3):
    """
    Combines 4 strings into a single data string to send via UDP
    Returns a string of 80 chars (4x20 bytes)
    """
    input_data = [row0, row1, row2, row3]
    data_to_send = ''
    print ('--------------------')
    for data in input_data:
        if len(data) > 20:
            print('Data too long for one row!')
            data = '{:<20}'.format('invalid data')
        else:
            data_to_send = data_to_send + '{:<20}'.format(data)
            print (data)
    print ('--------------------')
    return data_to_send

def update_LCD(data_to_send, print_ack = False):
    if (len(data_to_send) != 80):
        print ("update_LCD: incorrect data size")
    else:
        sock.sendto(data_to_send, (RECEIVER_IP, RECEIVER_PORT))
        received_data, from_socket = sock.recvfrom(BUFFER_SIZE)
        if (print_ack): print("{} from {}".format(received_data,from_socket))
        return

UPDATE_INTERVAL = 1.000  # intveral betwen display updates in seconds
if __name__ == '__main__':
    t_inc = time.time()
    n = 1
    while True:
        data_to_send = make_data_to_send('row1', '', '', 'increment {}'.format(n))
        update_LCD(data_to_send)
        t_inc = t_inc + UPDATE_INTERVAL
        n = n + 1
        time.sleep(max(0, t_inc - time.time()))
    sock.close()
