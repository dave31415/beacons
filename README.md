beacons
=======

Some experiments on the detection of iBeacons

Using 5 Kontakt beacons

Download and install the following App first 

https://github.com/dave31415/BeaconScanner

That scans for iBeacons and logg them to a file

This repo requires tailer and Flask. 

sudo pip install tailer

sudo pip install Flask

and numpy and matplotlib

Make a PARAMS file (which is in the .gitignore)

cp PARAMS_DEFAULT PARAMS

and edit that file as needed.  

You may need to create a file 'api.key' if you are running the server on a remote machine
such as on AWS. Also keep in .gitignore

Now, lets run the logger!

python logger.py

This will print out the url which is by default http://localhost:7979
Don't visit this url immediately. 

This app will now be waiting for REST calls from the publisher and the BeaconScanner App will be logging 
data to your logfile. Now we will start the publisher which will "tail" that logfile annd send new data to the
webapp which will store the data in SQLLite and make charts. Start this with 

python publish.py

or specify the logfile and url specifically, e.g. 

python publisher.py /path/to/log http://ec2.myserver.aws.com

This will connect the circuit. Wait a few seconds for some data to build up and then
visit the url with your browser. You should see a webpage with a chart at the top and some information 
and a table of the data below.



