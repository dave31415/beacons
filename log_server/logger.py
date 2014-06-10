# all the imports
from __future__ import with_statement
import sqlite3
from contextlib import closing
from flask import Flask, request, g, url_for, render_template
import json
import time
from time import mktime
from datetime import datetime
from lowess_tmp import lowess
import numpy as np
import smoothing

from PARAMS import *

#important parameters and defaults

DEBUG = True
SHOW_MAX=100
F_LOWESS=0.1
STATS_WINDOW_SEC=15
ERR_MIN=0.05
REFRESH_RATE_SEC=5000000000
SMOOTHING_TYPE='windowed'
BOX_SM_SEC=20.0
SS_ZPT=100
TIME_SUBTRACT=698000+14500
NO_SIGNAL_VALUE=0.3
JITTER=0.3
SHOW_ALL="yes"

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

JSON_DC=json.JSONDecoder()
JSON_EC=json.JSONEncoder()

def epoch_from_ts(ts="Jun 05 11:31:20",sub=False):
    ts="2014 "+ts
    time_st=time.strptime(ts,'%Y %b %d %H:%M:%S')
    ep=mktime(time_st)
    if sub:
        start_ts=ts="Jun 01 00:00:00"
        ep_start=epoch_from_ts(start_ts,sub=False)
        ep=ep-ep_start
    return ep
    
def integerify(some_list):
    return  some_list
    for i,l in enumerate(some_list):
        if isinstance(l,list) : l=integerify(l)
        if isinstance(l,float) or isinstance(l,int): 
            print 'float',l
            some_list[i]=float("%0.1f" % i)
    return some_list

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_lookup():
    file='mac_look.json'
    JSON_DC=json.JSONDecoder()
    return JSON_DC.decode(open(file,'rU').read())

def add_mac(d,lookup=None):
    if lookup == None: lookup=get_lookup()
    key_sep='_'
    key=key_sep.join(['UUID',d['uuid'],'Major',str(d['major']),'Minor',str(d['minor'])])
    if key in lookup:
        value=lookup[key]     
        d['MAC']=value['MAC']
    else :
        print "warning key %s not found" % key
        d['MAC']=abs(hash(key))
    d['ss']=str(SS_ZPT+int(d['rssi']))
    d['epoch']=epoch_from_ts(d['date_str'],sub=True)
    return d

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route('/',methods=['POST','GET'])
def chart_latest():
    #form changable parameters
    message=request.form.get('message', '') 
    showmax=int(request.form.get('showmax', SHOW_MAX))
    smoothing_type=request.form.get('smoothing_type', SMOOTHING_TYPE)
    f_lowess=float(request.form.get('f_lowess', F_LOWESS))
    box_sm_sec=float(request.form.get('box_sm_sec', BOX_SM_SEC))
    refresh_rate_sec=int(request.form.get('refresh_rate_sec', REFRESH_RATE_SEC))
    showall=request.form.get('showall', SHOW_ALL)

    #TODO: careful about sorting by date string. Not correct!!  
    cur = g.db.execute('select * from entries order by date_str DESC limit %s'%showmax)
    entries = [add_mac(dict(id=row[0], uuid=row[1], major=row[2], minor=row[3], rssi=row[4], date_str=row[5])) for row in cur.fetchall()]
    #entries is a list of dicts, get unique MACs
    macs=list({e['MAC'] for e in entries})
    macs=sorted(macs)
    n_macs=len(macs)
    xs_dict={}
    columns_list=[]
    x_all=[]
    data_all=[]
    for i in xrange(n_macs) :
        ii=str(i)
        data_name="data"+ii
        x_name='x'+ii
        x=[e['epoch']-TIME_SUBTRACT+JITTER*np.random.randn() for e in entries if e['MAC']==macs[i]]
        dat=[int(e['ss']) for e in entries if e['MAC']==macs[i]]
        x_all=x_all+x
        data_all=data_all+dat
        
        if  showall == 'yes':
            xs_dict[data_name]=x_name
            columns_list.append([x_name]+x)
            columns_list.append([data_name]+dat)
        
    x_all=np.array(x_all)
    data_all=np.array(data_all)

    so=np.argsort(x_all)
    x_all=x_all[so]
    data_all=data_all[so]

    t_zeros=[]

    if smoothing_type == 'lowess' :
        data_smooth=lowess(x_all,data_all,f=f_lowess,iter=3)
    if smoothing_type == 'exponential' :
        data_smooth=smoothing.smooth_exp(data_all,scale=exp_sm_scale)
    if smoothing_type == 'windowed' :
        data_smooth,t_zeros = smoothing.smooth(x_all,data_all,B=box_sm_sec,beta=1.0)
        
    no_signal=[NO_SIGNAL_VALUE for i in t_zeros] 
    
    xs_dict['data_all']='x_all'
    columns_list.append(['x_all']+t_zeros+list(x_all))
    columns_list.append(['data_all']+no_signal+list(data_smooth))
    #a hack just for the colors
    columns_list=list(reversed(columns_list))
    
    time_last=x_all[-1]
    window=x_all > (time_last-STATS_WINDOW_SEC)
    
    ss_mean="%0.1f" % data_all[window].mean()
    ss_sigma="%0.2f" % np.sqrt(data_all[window].std()**2 + ERR_MIN**2)
    ss_mean_smooth="%0.1f" % data_smooth[window].mean()
    ss_sigma_smooth="%0.2f" % np.sqrt(data_smooth[window].std()**2+ERR_MIN**2)

    dist_m_numeric=smoothing.dist_power_law(float(ss_mean_smooth)-SS_ZPT)
    dist_m="%0.2f" % dist_m_numeric

    return render_template('log_charts.html', entries=entries,xs=xs_dict,columns=columns_list,ss_mean=ss_mean,ss_sigma=ss_sigma,
                           ss_mean_smooth=ss_mean_smooth,ss_sigma_smooth=ss_sigma_smooth,message=message, dist_m=dist_m,
                           showmax=showmax,smoothing_type=smoothing_type,f_lowess=f_lowess,box_sm_sec=box_sm_sec,
                           showall=showall,
                           refresh_rate_sec=refresh_rate_sec)

@app.route('/all')
def show_all():
    cur = g.db.execute('select * from entries order by date_str DESC')
    entries = [add_mac(dict(id=row[0], uuid=row[1], major=row[2], minor=row[3], rssi=row[4], date_str=row[5])) for row in cur.fetchall()]
    return render_template('log_all.html', entries=entries)

@app.route('/submit', methods=['POST'])
def submit_entry():
    print "submission received"
    g.db.execute('insert into entries (uuid, major,minor,rssi,date_str) values (?, ?, ?, ?, ?)',
            [request.form['uuid'], request.form['major'], request.form['minor'], request.form['rssi'], request.form['date_str']])
    g.db.commit()
    print "submission entered'"
    return 'this is ok'

if __name__ == '__main__':
    app.run(port=PORT)
