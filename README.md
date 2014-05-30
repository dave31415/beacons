beacons
=======

Some experiments on the detection of iBeacons

Using 5 Kontakt beacons

Detections made with iBeaconDetector android app

Main conclusions so far:

1. My iBeacons are very noisy. One has to average the signal over 10 seconds or so 
to get a reasonably accurate measurement. 

2. There is a lot of refection and absorption. The signal indoors is corrupted by this
for better or worse. 

3. The signal drops off extremely rapidly. Power drops off with distance with power-law decay exponents
of 20-40 compared to 2 for typical inverse square law loss (over a couple of meters). 

4. In a typical indoor enviroment, a single beacon can basically only tell you whether you are ‎in 
one of three groups.

1) (RSSI > -50) You are probably within a meter or two.
2) (-100 < RSSI < -50) You are probably more than a meter away but less than 10 meters.
3) (No signal) You are defintely not within 3 meters and probably not within 5 meters.  




