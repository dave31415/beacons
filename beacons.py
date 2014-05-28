import requests, json

base_url="http://api.kontakt.io/"
api_key=open('api.key','r').read()
unique_ids=['dFTG','DuOP','cYOy','aqO9','HMGV']
#DC=json.JSONDecoder()

def get_beacons(num=0):
    url=base_url+'beacon/'+unique_ids[num] 
    headers=headers = {'content-type': 'application/json','Api-Key':api_key}
    r = requests.get(url,headers=headers)
    content=r.json()
    return content
  



