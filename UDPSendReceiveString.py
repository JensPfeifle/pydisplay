import socket
import time
import httplib
import requests

LCD_CONNECTED = True

BUFFER_SIZE = 1024
UDP_IP = '192.168.2.1'
UDP_PORT = 6000

RECEIVER_IP = '192.168.2.2'
RECEIVER_PORT = 8888

if LCD_CONNECTED:
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

def netdata_api_request(host='jens.pfeifle.com/netdata', chart='system.cpu'):
    r = requests.get('http://{}/api/v1/data?chart={}&after=-16&before=0&points=16&group=average&format=json&options=seconds'
                    .format(host, chart))
    if r.status_code != 200:
        print ("Status not 200: code {}".format(r.status_code))
    else:
        return r.json()


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
            print(data + '<== truncated')
            data = data[:20]
        else:
            print (data)
        data_to_send = data_to_send + '{:<20}'.format(data)
    print ('--------------------')
    return data_to_send

def update_LCD(data_to_send, print_ack = False):
    if (len(data_to_send) != 80):
        print ("update_LCD: incorrect data size")
        return False
    else:
        sock.sendto(data_to_send, (RECEIVER_IP, RECEIVER_PORT))
        if (print_ack):
            received_data, from_socket = sock.recvfrom(BUFFER_SIZE)
            print("{} from {}".format(received_data,from_socket))
        return True

def num_to_bar(value, minval=0, maxval=1.0):
    bar_symbol = '='
    fraction_value = value/(maxval - minval)  # careful floor division
    bar_length = int(round(fraction_value * 20,0))
    bar = ''
    for n in range(bar_length):
        bar = bar + bar_symbol
    return bar

UPDATE_INTERVAL = 1.000  # intveral betwen display updates in seconds
HOST = 'localhost:19999'
if __name__ == '__main__':
    t_inc = time.time()
    n = 1
    while True:
        # cpu data
        data_cpu = netdata_api_request(host=HOST,chart='system.cpu')
        sum_cpu = round(sum(data_cpu['data'][0][1:]),2)
        # ipv4 network data
        data_ipv4 = netdata_api_request(host=HOST, chart='system.ipv4')
        ipv4_in = int(round(data_ipv4['data'][0][1],0))
        ipv4_out = int(abs(round(data_ipv4['data'][0][2],0)))
        #
        data_to_send = make_data_to_send(HOST,
                                        'i:{:>5} o:{:>5} kb/s'.format(ipv4_in, ipv4_out),
                                        num_to_bar(sum_cpu,maxval=100.0),
                                        '{}'.format(time.strftime("%d/%m/%y %H:%M:%S"))
                                        )
        if (LCD_CONNECTED): update_LCD(data_to_send)
        t_inc = t_inc + UPDATE_INTERVAL
        n = n + 1
        time.sleep(max(0, t_inc - time.time()))
    sock.close()
