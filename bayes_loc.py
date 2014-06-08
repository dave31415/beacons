import numpy as np

def signal_strength(dist_m):
    #signal strength versus distance
    cm=0.01
    beta=18.0
    dist_use=np.sqrt(dist_m**2 + cm**2)
    T1=-77.0
    RSSI = T1  - beta*np.log10(dist_use)
    SS=100+RSSI
