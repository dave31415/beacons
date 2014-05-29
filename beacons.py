import requests, json
import urllib, urllib2, cookielib, socket
import csv, glob
from collections import defaultdict
from matplotlib import pylab as plt
import numpy as np

base_url="http://api.kontakt.io/"
api_key=open('api.key','r').read().strip()
root_dir='/home/davej/beacons'

data_dir=root_dir+'/data'
plot_dir=root_dir+'/plots'

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
    data={'uniqueId':uid,
    'password':'goodnight','interval':130}
    
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
    for d in data:
        mac=d['MAC Addr']
        d.update(mac_lookup[mac])
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
    
def plot_all(sub_dir='Stack2m'):
    data=read_all(sub_dir)
    legs=[]
    mean_rssi=[]
    mean_rssi_err=[]
    max_x=0
    xextra=10
    fig=plt.figure()
    for name,dat in data.iteritems():
        num=len(dat)
        max_x=max(max_x,num)
        print name
        legs.append(name)
        ts=[i['Last Updated'] for i in dat]
        rssi=np.array([float(i['RSSI']) for i in dat])
        print ts
        print rssi
        mean_rssi.append(rssi.mean())
        mean_rssi_err.append(rssi.std()/np.sqrt(num))
        x=np.arange(num)
        plt.plot(x,rssi,linewidth=3)
    for m,merr in zip(mean_rssi,mean_rssi_err):
        plt.hlines(m,0,num+10,linestyle='--')
        plt.hlines(m-merr,0,num+xextra,linestyle='dotted')
        plt.hlines(m+merr,0,num+xextra,linestyle='dotted')        
        plt.fill_between([0,num+xextra],m+merr,m-merr,alpha=0.2)
    plt.xlim=(0,max_x+20)
    plt.ylabel('Signal Strength  ( RSSI )')
    plt.xlabel('Iteration')
    plt.legend(legs)
    plt.title(sub_dir)
    fig.savefig(plot_dir+'/'+sub_dir+'_rssi.png')
    #plt.show()    

def plot_all_subs():
    sub_dirs=glob.glob(data_dir+'/*')     
    for sub_full in sub_dirs:
        sub=sub_full.split('/')[-1]
        print sub
        plot_all(sub)        




