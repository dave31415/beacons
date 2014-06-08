import numpy as np
from matplotlib import pylab as plt
from matplotlib.cbook import flatten

beta_def=17.5

def smooth_exp(x,y,scale=10.0,N=4):
    #smooth with expoential tail backwards in time
    #should be sorted by x
    xrev=np.array(x)[::-1]
    yrev=np.array(y)[::-1]
    size=np.ceil(scale*N)
    weight=np.exp(-np.arange(size)/scale)
    yrev_sm=yrev*0.0
    for i,xi in enumerate(xrev):
        x_window=xrev[i:i+scale*N]
        y_window=yrev[i:i+scale*N]
        #normalize, could be truncated
        w=weight[0:len(x_window)]
        w=w/w.sum()
        yrev_sm[i]=(y_window*w).sum()
    y_sm=yrev_sm[::-1]
    return y_sm

def RSSI_power_law(dist_m,beta=beta_def):
    RSSI=-77.0-beta*np.log10(dist_m)
    return RSSI

def dist_power_law(RSSI,beta=beta_def):
    dist_m = 10.0**((RSSI+77)/(-beta))
    return dist_m

def prob_dist(RSSI,dist_m,beta=beta_def,sig_RSSI=5.0,number=1.0):
    #lognormal
    if RSSI < -100 : return RSSI*0.0
    R_sig=sig_RSSI/np.sqrt(number)
    RSSI_mean=RSSI_power_law(dist_m,beta=beta)
    gauss=np.exp(-0.5*((RSSI-RSSI_mean)/R_sig)**2)
    return gauss

def grocery_store_im():
    import matplotlib.image as mpimg
    file="/Users/davej/Desktop/GrocStore.png"
    img=mpimg.imread(file)
    return img

def prob_grid():
    im_store=grocery_store_im()
    im=im_store.copy()
    shape=im.shape
    plt.imshow(im)
    print shape
    nx=shape[0]
    ny=shape[1]
    print nx*ny
    x=np.array([np.arange(nx) for i in xrange(ny)]).flatten()
    y=np.array([np.repeat(i,nx) for i in xrange(ny)]).flatten()

    imflat=[]
    for plane in range(3):
        f=(im[0:,0:,plane]).flatten()
        print f.shape
        imflat.append(f)

    xc=nx/2.0
    yc=ny/2.0
    rad=100.0
    mask=np.sqrt((x-xc)**2 + (y-yc)**2 ) < rad
    #return mask, x,y,imflat

    imflat_g=imflat[0]
    imflat_g[mask]=0.5
    imflat_g.shape=(nx,ny)

    im[0:,0:,0]=imflat_g
    plt.imshow(im)


    









