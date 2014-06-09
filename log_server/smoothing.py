import numpy as np
from matplotlib import pylab as plt
from matplotlib.cbook import flatten

beta_def=17.5

def smooth_exp(y,scale=10.0,N=4):
    #smooth with expoential tail
    yrev=np.array(y)[::-1]
    size=np.ceil(scale*N)
    weight=np.exp(-np.arange(size)/scale)
    yrev_sm=yrev*0.0
    for i in xrange(len(y)):
        y_window=yrev[i:i+scale*N]
        #normalize, might be truncated
        w=weight[0:len(y_window)]
        w=w/w.sum()
        yrev_sm[i]=(y_window*w).sum()
    y_sm=yrev_sm[::-1]
    return y_sm

def smooth_exp_xy(x,y,scale=10.0,N=4):
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

def filter_window_PL(x,B,beta=0.0,plot=False):    
    '''filter for smoothing, B is the Box size. 
    beta=0.0 : box-car smoothing
    beta=1.0 : straight line from 1 to 0
    beta=4.5 : approximate exponential smoothing with scale ~ B/5
    '''
    rat=(x/float(B))
    filter=(1.0-rat)**beta
    filter[(x>B) | (x<0)]=0.0
    if plot : plt.plot(x,filter)
    return filter

def windowed_mean(t,y,B,t_point=None,beta=0.3):
    if t_point == None:
        t_point=t.max()
    x=t_point-t    
    weight=filter_window_PL(x,B,beta=beta)
    weight /= weight.sum()
    return (weight*y).sum()

def smooth(t,y,B=10.0,beta=0.3,plot=False):
    sm=y*0.0
    assert(B>0)
    for i,t_point in enumerate(t):
        sm[i]=windowed_mean(t,y,B,t_point=t_point,beta=beta)
    if plot:
        plt.plot(t,y)
        plt.plot(t,sm)
    return sm








