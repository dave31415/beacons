import requests, json
import urllib, urllib2, cookielib, socket

base_url="http://api.kontakt.io/"
api_key=open('api.key','r').read().strip()
unique_ids=['dFTG','DuOP','cYOy','aqO9','HMGV']

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
    
    
    
    
    
    