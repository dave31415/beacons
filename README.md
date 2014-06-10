beacons
=======

Some experiments on the detection of iBeacons

Using 5 Kontakt beacons

Download and install this first which is an App to scan for iBeacons and log the results to a file. 

https://github.com/dave31415/BeaconScanner

This repo requires tailer and Flask. 

sudo pip install tailer

sudo pip install Flask

and numpy and matplotlib

cd log_server

python logger.py

This will print out the url which is by default http://localhost:7979
Don't visit this url immediately. 

This app will now be waiting for REST calls from the publisher and the BeaconScanner App will be logging 
data to your logfile. Now we will start the publisher which will "tail" that logfile annd send new data to the
webapp. Start this with 

python publish.py

or specify the logfile and url specifically, e.g. 

python publisher.py /path/to/log http://ec2.myserver.aws.com

This will connect the circuit. Wait a few seconds for some data to build up and then
visit the url with your browser. You should see a webpage with a chart at the top and some information 
and a table below that of the data. 

