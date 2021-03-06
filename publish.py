'''
Follow the beacon log file created by C# logging application
and send any updates to the API that keeps all the logs
syntax :
python publish.py [logfile] [url]
'''

import sys
import tailer
from publisher import publish_it

nitems=5
route='/submit'

#base_url_def="http://ec2-54-184-199-186.us-west-2.compute.amazonaws.com"
base_url_def="http://localhost:7979"

if len(sys.argv) > 1:
    file_to_follow=sys.argv[1]
else :
    file_to_follow="/var/log/iBeacons.log"

if len(sys.argv) > 2:
    base_url=sys.argv[2]
else :
    base_url=base_url_def

url=base_url+route
print "collecting data from %s and sending to url %s" %(file_to_follow, url)

def publish_5(line):
    data=line.split(',')
    if len(data) != nitems:
        print "Warning did not find %s comma separated items. Skipping line." % nitems
    else :
        uuid,major,minor, rssi, date_str = data
        publish_it(url=url,uuid=uuid,major=major,minor=minor,rssi=rssi,date_str=date_str)

my_call_back=publish_5

for line in tailer.follow(open(file_to_follow)):
    my_call_back(line)
