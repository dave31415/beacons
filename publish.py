import sys
import tailer
from publisher import publish_it

nitems=5
url='http://localhost:7979/submit'

if len(sys.argv) > 1:
    file_to_follow=sys.argv[1]
else :
    file_to_follow="/var/log/iBeacons.log"

print "collecting data from %s"%file_to_follow
 

def my_call_back(line):
    #print line
    data=line.split(',')
    if len(data) != nitems:
        print "Warning did not find %s comma separated items. Skipping line." % nitems
    else :
        uuid,major,minor, rssi, date_str = data
        res=publish_it(url=url,uuid=uuid,major=major,minor=minor,rssi=rssi,date_str=date_str)
        print res

for line in tailer.follow(open(file_to_follow)):
    my_call_back(line)
