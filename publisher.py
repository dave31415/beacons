import requests, json
import urllib, urllib2, cookielib, socket
import random

url_local='http://localhost:7979/submit'
api_key="BlahBlah"


def publish_it(url=url_local,uuid='a77b',major=9999,minor=3333,rssi=-77,date_str='June 18 1975'):
    #publish some stuff to api
    headers = {"User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.46 Safari/535.11",
                "Accept-Charset" : "ISO-8859-1",
                "Content-type": "application/x-www-form-urlencoded"}
    
    headers['content-type']='application/x-www-form-urlencoded'
    headers['Api-Key']=api_key
    data={'uuid':uuid,'major':major,'minor':minor,'rssi':rssi,"date_str":date_str}
    #print data

    res=''
    try :
        req = urllib2.Request(url, urllib.urlencode(data), headers)
        opener = urllib2.build_opener()
        res = opener.open(req)
        res_code=res.getcode()
        res_text=res.read()
        if res_code != 200 :
            print "Warning reponse code %s is not 200" % res_code
        if res_text != "this is ok" :
            print "Warning unexpected response: %s" % res_text
    except:
        print "Error - Submission Unsuccessful"    
