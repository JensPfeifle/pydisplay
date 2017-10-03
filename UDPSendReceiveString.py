#!/usr/bin/env python
# coding: utf8
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

def netdata_api_request(host, chart='system.cpu', after=-1, before=0, points=1):
    """"
    Make a request to the Netdata API and return as a json file.
    host: given with protokoll and w/o trailing slash, i.e. 'http://my.host'
    chart: chart.id as given by 'charts' call
    after: after which point to get data (negative num is relative, in the past)
    before: up to which point to get data
    points: number of points to get
    """
    r = requests.get('{0}/api/v1/data?chart={1}&after={2}&before={3}&points={4}&group=average&format=json&options=seconds'
                    .format(host, chart, after, before, points))
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

def num_to_bar(value, minval=0, maxval=1.0, max_len=20):
    bar_symbol = '\xff'
    fraction_value = value/(maxval - minval)  # careful floor division
    bar_length = int(round(fraction_value * max_len))
    bar = ''
    for n in range(bar_length):
        bar = bar + bar_symbol
    return bar

UPDATE_INTERVAL = 1.0  # interval betwen display updates in seconds
#HOST = 'http://localhost:19999'
HOST = r'http://unjens:19999'
HOST_STR = 'UnJens'
if __name__ == '__main__':
    t_inc = time.time()
    n = 1
    while True:
        t0 = time.time()
        # cpu data
        data_cpu = netdata_api_request(host=HOST,chart='system.cpu')
        sum_cpu = round(sum(data_cpu['data'][0][1:]),2)
        # mem_data
        data_mem = netdata_api_request(host=HOST,chart='system.ram')
        used_mem = int(round(data_mem['data'][0][2]))
        # ipv4 network data
        data_ipv4 = netdata_api_request(host=HOST, chart='system.ipv4')
        ipv4_in = int(round(data_ipv4['data'][0][1],0))
        ipv4_out = int(abs(round(data_ipv4['data'][0][2],0)))
        #
        disks = ['sdb','sdc','sdd','sde']
        active = {}
        for d in disks:
            ddata = netdata_api_request(host=HOST, chart='disk_util.{}'.format(d), after=-1, points=1)  # average over the last 10 seconds
            active_pp = ddata['data'][0][1]
            if (active_pp > 80.0):
                active[d] = '\x05'
            elif (active_pp > 50.0):
                active[d] = '\x04'
            elif (active_pp > 20.0):
                active[d] = '\x03'
            elif (active_pp > 5.0):
                active[d] = '\x02'
            elif (active_pp > 1.0):
                active[d] = '\x01'
            else:
                active[d] = '\x06'
        t_req = (time.time() - t0)
        print ('Requests took:{} ms'.format(t_req * 1000))
        if (t_req > UPDATE_INTERVAL):
            time.sleep(t_req*1.5)
            t_inc = t_inc + t_req + t_req*1.5
        data_to_send = make_data_to_send('{:^20}'.format(
                                        HOST_STR + ' ' + time.strftime("%H:%M:%S")),
                                        'CPU:{:2.0f} MEM:{:5.0f}MB'.format(sum_cpu, used_mem),
                                        'D1'+active['sdc']+' C'+active['sdd'] + ' in: {:>5}kbs'.format(ipv4_in),
                                        'D2'+active['sdb']+' P'+active['sde'] + ' out:{:>5}kbs'.format(ipv4_out)
                                        )
        if (LCD_CONNECTED): update_LCD(data_to_send)
        t_inc = t_inc + UPDATE_INTERVAL
        n = n + 1
        time.sleep(max(0, t_inc - time.time()))
        print ('Complete cycle took:{} s'.format(time.time() - t0))
    sock.close()

    """ Parked expressions:
    '{}'.format(time.strftime("%d/%m/%y %H:%M:%S"))
    BLOCK '\xff'
    custom chars ' '+'\x01'+'\x02'+'\x03'+'\x04'+'\x05'+'\x06'+'\x07'
    """
