import requests
import time

def timer(host='https://jens.pfeifle.com/netdata', chart='system.cpu'):
    t0 = time.time()
    r = requests.get('{}/api/v1/data?chart={}&after=-16&before=0&points=16&group=average&format=json&options=seconds'
                    .format(host, chart))
    if r.status_code != 200:
        print ("Status not 200: code {}".format(r.status_code))
    else:
        return (time.time() - t0) * 1000
