import requests, json
import urllib, urllib2, cookielib, socket
import csv, glob
from collections import defaultdict
from matplotlib import pylab as plt
import numpy as np
from time import mktime
from datetime import datetime
import time
from lowess import lowess

base_url="http://api.kontakt.io/"
api_key=open('api.key','r').read().strip()
jit=0.1

root_dir='/home/davej/beacons'
#root_dir='/Users/davej/TW/beacons'

data_dir=root_dir+'/data'
plot_dir=root_dir+'/plots'

ts_start=1401384000

unique_ids=['dFTG','DuOP','cYOy','aqO9','HMGV']
names=['Bathroom','Bedroom','Boys room','Gwens Room','Kitchen']
macs=['E8:66:CA:46:29:D9','C0:80:69:E4:96:80','C0:36:4C:60:FB:7A','C4:02:3E:D6:FB:17','CB:42:69:CE:8C:14']
mac_lookup={}
for i in range(5):
    mac_lookup[macs[i]]={'mac':macs[i],'uid':unique_ids[i],'name':names[i]}

def get_beacons(num=0):
    url=base_url+'beacon/'+unique_ids[num] 
    headers=headers = {'content-type': 'application/json','Api-Key':api_key}
    r = requests.get(url,headers=headers)
    content=r.json()
    return content

def put_beacons(content,num=0):
    url=base_url+'beacon/' 
    headers=headers = {'content-type': 'application/json','Api-Key':api_key}
    r = requests.put(url,data=content,headers=headers)
    return r    
  
def get_actions(num=0):
    url=base_url+'action/'+unique_ids[num] 
    headers=headers = {'content-type': 'application/json','Api-Key':api_key}
    r = requests.get(url,headers=headers)
    return r

def post_beacons(num=0):
    uid=unique_ids[num]
    url=base_url+'beacon/'+uid
    headers=headers = {'content-type':'application/x-www-form-urlencoded','Api-Key':api_key}
    data={'uniqueId':uid,'password':'hello'}
    r = requests.post(url,data=data,headers=headers)
    return r    

def post2_beacons(num=0):
    uid=unique_ids[num]
    url=base_url+'beacon/'+uid
    headers = {"User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.46 Safari/535.11",
                "Accept-Charset" : "ISO-8859-1",
                "Content-type": "application/x-www-form-urlencoded"}
    
    headers['content-type']='application/x-www-form-urlencoded'
    headers['Api-Key']=api_key
    data={'uniqueId':uid,'password':'goodnight','interval':99,'major':(num+1)*100000,'minor':0}
    

    req = urllib2.Request(url, urllib.urlencode(data), headers)
    
    # setup socket connection timeout
    timeout = 15
    socket.setdefaulttimeout(timeout)

    # setup cookie handler
    cookie_jar = cookielib.LWPCookieJar()
    cookie = urllib2.HTTPCookieProcessor(cookie_jar)
    
    opener = urllib2.build_opener()
    res = opener.open(req)
    return res
    
def read_csv_dump(filename,sub_dir):
    file_name=data_dir+'/'+sub_dir+'/'+filename
    data=list(csv.DictReader(open(file_name,'rU')))
    #filter out non-ibeacons for now
    data=[d for d in data if d['iBeacon flag'] == 'true'] 
    latest_measurement_time=0.0
    for d in data:
        mac=d['MAC Addr']
        d.update(mac_lookup[mac])   
        d['SS']=100.0+float(d['RSSI'])
        #get the time, have to remove fraction of second, keep it anyway on epoch
        date_time=d['Last Updated']
        dt=date_time.split('.')
        dt_round=dt[0]
        dt_frac=dt[1]
        time_st=time.strptime(dt_round,'%Y-%m-%d %H:%M:%S')
        frac_secs=float('.'+dt_frac)
        jitter=np.random.randn()*jit
        d['epoch']=mktime(time_st)+frac_secs+jitter
        d['datetime']=datetime.fromtimestamp(d['epoch'])
        latest_measurement_time=max(latest_measurement_time,d['epoch'])
    for d in data:
        d['last_time_file']=latest_measurement_time
        d['delayed_time']=d['last_time_file']-d['epoch']
    return data       


def read_all(sub_dir='Stack2m'):
    files=glob.glob(data_dir+'/'+sub_dir+'/*')        
    dat=defaultdict(list)

    for f in files:
        filename=f.split('/')[-1]
        data=read_csv_dump(filename,sub_dir)
        for line in data:    
            name=line['name']
            dat[name].append(line)
    return dat
    
def smooth_ts(ts,Y):
    #smooth a signal
    s=np.argsort(ts)    
    ts_s=ts[s]
    Y_s=Y[s]
    pass


def plot_all(sub_dir='Stack2m',delay_max=4,doleg=True,f_lowess=0.15,dolowess=True,showplot=True):
    data=read_all(sub_dir)
    legs=[]
    mean_ss=[]
    mean_ss_err=[]
    max_x=0
    xextra=10
    fig=plt.figure()
    ts_all=[]
    SS_all=[]
    for name,dat in data.iteritems():
        num=len(dat)
        max_x=max(max_x,num)
        print name
        legs.append(name)
        ts=np.array([i['epoch'] for i in dat if i['delayed_time'] < delay_max])
        SS=np.array([i['SS'] for i in dat if i['delayed_time'] < delay_max])
        mean_ss.append(SS.mean())
        mean_ss_err.append(SS.std()/np.sqrt(num))
        x=ts-ts_start        
        o=np.argsort(x)
        plt.plot(x[o],SS[o],'o-')
        ts_all=ts_all+list(x)
        SS_all=SS_all+list(SS)  
    #return ts_all,SS_all
    ts_all=np.array(ts_all)
    SS_all=np.array(SS_all)
    o=np.argsort(ts_all)
    ts_all=ts_all[o]
    SS_all=SS_all[o] 
    #return ts_all,SS_all
    if dolowess:    
        smooth=lowess(ts_all,SS_all,f_lowess)
        plt.plot(ts_all,smooth,'-',linewidth=3)

    for m,merr in zip(mean_ss,mean_ss_err):
        #plt.hlines(m,0,num+10,linestyle='--') 
        #plt.hlines(m-merr,0,num+xextra,linestyle='dotted')
        #plt.hlines(m+merr,0,num+xextra,linestyle='dotted')        
        #plt.fill_between([0,num+xextra],m+merr,m-merr,alpha=0.2)
        pass    

    plt.ylabel('Signal Strength  = RSSI +100')
    plt.xlabel('Seconds')

    if doleg:    
        legs_full=[leg +  " : "+'%0.2f'%m+' +/- ' +'%0.1f'%e for leg,m,e in zip(legs,mean_ss,mean_ss_err)]        
        plt.legend(legs_full)
    
    plt.title(sub_dir)
    if showplot: plt.show()  

    fig.savefig(plot_dir+'/'+sub_dir+'_ss.png')
    
def plot_all_subs():
    sub_dirs=glob.glob(data_dir+'/*')
    for sub_full in sub_dirs:
        sub=sub_full.split('/')[-1]
        print sub
        plot_all(sub,dolowess=False,showplot=False)

def proc_range(sub_dir='Range0.5to4mby0.5',delay_max=3.0,noise_floor=4.0,min_plot=-4.0):
    break_points=[700,770,818,871,915,965,1015,1070,1200]
    distance_m=np.array([0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0])
    fin=break_points[1:]
    sta=break_points[0:-1]    

    data=read_all(sub_dir)    
    legs=[]
    mean_ss=[]
    mean_ss_err=[]
    max_x=0
    xextra=10
    fig=plt.figure()
    dist_data={}
    for name,dat in data.iteritems():
        num=len(dat)
        max_x=max(max_x,num)
        print name
        legs.append(name)
        ts=np.array([i['epoch'] for i in dat if i['delayed_time'] < delay_max])
        SS=np.array([i['SS'] for i in dat if i['delayed_time'] < delay_max])
        mean_ss.append(SS.mean())
        mean_ss_err.append(SS.std()/np.sqrt(num))
        x=ts-ts_start        
        o=np.argsort(x)
        X=x[o]
        Y=SS[o]
        plt.plot(X,Y,'o')
        t_mean_bin=[]
        ss_mean_bin=[]
        ss_mean_bin_err=[]
        for first,last in zip(sta,fin):
            inbin=(X>first)* (X<last)
            XX=X[inbin]
            YY=Y[inbin]
            t_mean_bin.append(XX.mean())
            ss_mean_bin.append(YY.mean())                 
            num_pt=len(YY)
            YY_err=YY.std()/np.sqrt(num_pt)
            corr=(num_pt/(num_pt-1.0+0.1))
            print name,num_pt
            YY_err=YY_err*corr
            
            ss_mean_bin_err.append(YY_err)
        #plt.plot(t_mean_bin,ss_mean_bin,'ok-',markersize=15)
        dist_data[name]=[ss_mean_bin,ss_mean_bin_err]

    for bp in break_points:
        plt.vlines(bp,-5,50)    

    plt.ylabel('Signal Strength  = RSSI +100')
    plt.xlabel('Seconds')
    
    legs_full=[leg +  " : "+'%0.2f'%m+' +/- ' +'%0.1f'%e for leg,m,e in zip(legs,mean_ss,mean_ss_err)]        
    plt.legend(legs_full)
    plt.title(sub_dir)
    #fig.savefig(plot_dir+'/'+sub_dir+'_ss.png')
    plt.show()   
    fig2=plt.figure()
    leg_dist=[]
    for name,ss_mean_data in dist_data.iteritems():
        ss_mean_val=ss_mean_data[0]
        ss_mean_val_err=ss_mean_data[1]
        corrected_exp=np.exp(ss_mean_val)-np.exp(noise_floor)
        corrected_exp[corrected_exp < np.exp(min_plot)]=np.exp(min_plot)
        ss_mean_val_correct=np.log(corrected_exp)
        plt.plot(np.log10(distance_m),ss_mean_val_correct,'o-',markersize=10)
        #plt.errorbar(distance_m,ss_mean_val,xerr=0.1,yerr=ss_mean_val_err)
        leg_dist.append(name)
    for name,ss_mean_data in dist_data.iteritems():
        ss_mean_val=ss_mean_data[0]
        ss_mean_val_err=ss_mean_data[1]
        #plt.plot(distance_m,ss_mean_val,'o-')
        #plt.errorbar(np.log10(distance_m),ss_mean_val,xerr=0.1,yerr=ss_mean_val_err)    
        
    plt.xlabel('Log Distance (m)')
    xfid=np.linspace(-0.5,0.5,30)
    plt.plot(xfid,xfid*0.0+noise_floor,linestyle='dashed')
    zpt=20.0
    slope=2.0
    plt.plot(xfid,zpt-slope*xfid,linewidth=5,linestyle='--')
    slope=40.0
    plt.plot(xfid,zpt-slope*xfid,linewidth=5,linestyle='--')
    fig2.savefig(plot_dir+'/ranging_test.png')
    

    plt.legend(leg_dist)
    plt.show()
    
def proc_range2(sub_dir='Range5to.5mby.5',delay_max=3.0,noise_floor=8.0,min_plot=-4.0):
    break_points=[160,215,269, 317, 369,418,465,521,576,624,716]
    distance_m=np.array([5.0,4.5,4.0,3.5,3.0,2.5,2.0,1.5,1.0,0.5])
    fin=break_points[1:]
    sta=break_points[0:-1]    

    data=read_all(sub_dir)    
    legs=[]
    mean_ss=[]
    mean_ss_err=[]
    max_x=0
    xextra=10
    fig=plt.figure()
    dist_data={}
    for name,dat in data.iteritems():
        num=len(dat)
        max_x=max(max_x,num)
        print name
        legs.append(name)
        ts=np.array([i['epoch'] for i in dat if i['delayed_time'] < delay_max])-71600
        SS=np.array([i['SS'] for i in dat if i['delayed_time'] < delay_max])
        mean_ss.append(SS.mean())
        mean_ss_err.append(SS.std()/np.sqrt(num))
        x=ts-ts_start        
        o=np.argsort(x)
        X=x[o]
        Y=SS[o]
        plt.plot(X,Y,'o')
        t_mean_bin=[]
        ss_mean_bin=[]
        ss_mean_bin_err=[]
        for first,last in zip(sta,fin):
            inbin=(X>first)* (X<last)
            XX=X[inbin]
            YY=Y[inbin]
            t_mean_bin.append(XX.mean())
            ss_mean_bin.append(YY.mean())                 
            num_pt=len(YY)
            YY_err=YY.std()/np.sqrt(num_pt)
            corr=(num_pt/(num_pt-1.0+0.1))
            print name,num_pt
            YY_err=YY_err*corr
            
            ss_mean_bin_err.append(YY_err)
        #plt.plot(t_mean_bin,ss_mean_bin,'ok-',markersize=15)
        dist_data[name]=[ss_mean_bin,ss_mean_bin_err]

    for bp in break_points:
        plt.vlines(bp,-5,50)    

    plt.ylabel('Signal Strength  = RSSI +100')
    plt.xlabel('Seconds')
    
    legs_full=[leg +  " : "+'%0.2f'%m+' +/- ' +'%0.1f'%e for leg,m,e in zip(legs,mean_ss,mean_ss_err)]        
    #plt.legend(legs_full)
    plt.title(sub_dir)
    #fig.savefig(plot_dir+'/'+sub_dir+'_ss.png')
    plt.show()   
    fig2=plt.figure()
    leg_dist=[]
    for name,ss_mean_data in dist_data.iteritems():
        ss_mean_val=ss_mean_data[0]
        ss_mean_val_err=ss_mean_data[1]
        corrected_exp=np.exp(ss_mean_val)-np.exp(noise_floor)
        corrected_exp[corrected_exp < np.exp(min_plot)]=np.exp(min_plot)
        ss_mean_val_correct=np.log(corrected_exp)
        plt.plot(np.log10(distance_m),ss_mean_val_correct,'o-',markersize=10)
        #plt.errorbar(distance_m,ss_mean_val,xerr=0.1,yerr=ss_mean_val_err)
        leg_dist.append(name)
    for name,ss_mean_data in dist_data.iteritems():
        ss_mean_val=ss_mean_data[0]
        ss_mean_val_err=ss_mean_data[1]
        #plt.plot(distance_m,ss_mean_val,'o-')
        #plt.errorbar(np.log10(distance_m),ss_mean_val,xerr=0.1,yerr=ss_mean_val_err)    
        
    plt.xlabel('Log Distance (m)')
    xfid=np.linspace(-0.5,0.5,30)
    plt.plot(xfid,xfid*0.0+noise_floor,linestyle='dashed')
    zpt=23.0
    slope=2.0
    plt.plot(xfid,zpt-slope*xfid,linewidth=5,linestyle='--')
    slope=25.0
    plt.plot(xfid,zpt-slope*xfid,linewidth=5,linestyle='--')
    fig2.savefig(plot_dir+'/ranging_5m_to_0.5m_by0.5m.png')

    plt.legend(leg_dist)
    plt.show()
    
        






