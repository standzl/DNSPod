#!/usr/bin/python
#-*- coding:utf-8 -*-

import httplib, urllib
import socket
import time
import logging
import logging.handlers
import sys
import json
import copy
import threading

#try to get initial ip on dnspod every tick until success
GET_INITIAL_IP_TICK = 10 
#check ip every tick
CHECK_IP_TICK = 10

#log file handler
#--------------------------you need to change your log file
logFile = '/home/pi/DNSPod/ddp.log'
handler = logging.handlers.RotatingFileHandler(logFile, maxBytes = 1024*1024, backupCount=10)
#fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(message)s'
formatter = logging.Formatter(fmt)
handler.setFormatter(formatter)

#log console handler
console = logging.StreamHandler()
console.setFormatter(formatter)

#register handler to logger
logger = logging.getLogger('ddp')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.addHandler(console)

#params used to query initial ip
#-----------------------you need to change your params
paramsQuery = dict(
    login_token="30201,77cdcdf7c78a5c94e14aaa2d2c7a9070", # replace with your email
    lang="cn", 
    format="json",
    domain_id="2394741", # replace with your domain_od, can get it by API Domain.List
    record_id="47014600", # replace with your record_id, can get it by API Record.List
)

#params used to update ip to dnspod
#-----------------------you need to change your params
params = copy.deepcopy(paramsQuery)
params.update({"sub_domain":"sub_domain", "record_line":"默认"})

#current ip in dnspod
currentIP = None
#init thread Condition
con=threading.Condition()

#query initial ip from dnspod
def getInitialIPFromDP():
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/json"}
    conn = httplib.HTTPSConnection("dnsapi.cn")
    conn.request("POST", "/Record.Info", urllib.urlencode(paramsQuery), headers)
    response = conn.getresponse()
    logger.info('response from dnspod: %s %s', response.status, response.reason)
    data = response.read()
    logger.info('data from dnspod: %s', data)
    datajson = json.loads(data)
    conn.close()
    return datajson['record']['value']


#get local server ip
def getServerIP():
    sock = socket.create_connection(('ns1.dnspod.net', 6666))
    ip = sock.recv(16)
    sock.close()
    return ip


#update ip to dnspod
def UpdateIPToDP(ip):
    params.update(dict(value=ip))
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/json"}
    conn = httplib.HTTPSConnection("dnsapi.cn")
    conn.request("POST", "/Record.Ddns", urllib.urlencode(params), headers)
    response = conn.getresponse()
    logger.info('response from dnspod: %s %s', response.status, response.reason)
    data = response.read()
    logger.info('data from dnspod: %s', data)
    conn.close()
    return response.status == 200

# this is fetch ip Thread
def fetchIpThread():
	global currentIp
	if con.acquire():
		while True:
			try:
				logger.info('try to get initial ip from dnspod')
				currentIP = getInitialIPFromDP()
				if currentIP != None:
					logger.info('get initial ip: %s', currentIP)
					con.notify()
					con.wait()
				time.sleep(GET_INITIAL_IP_TICK)
			except Exception, e:
				logger.exception(e)
				pass
				
				

#This is update ip to dnspos Thread
def updateDnsposThread():
	global currentIP
	if con.acquire():
		while True:
			try:
				logger.info('start check ip')
				serverIP = getServerIP()
				logger.info('get server ip: %s. old: %s', serverIP, currentIP)
				if currentIP != serverIP:
					logger.info('ip changed, try to update new ip to dnspod')
					if UpdateIPToDP(serverIP):
						currentIP = serverIP
						logger.info('succeed')
				con.notify()
				con.wait()
				time.sleep(CHECK_IP_TICK)	
			except Exception, e:
				logger.exception(e)
				pass	
			

if __name__ == '__main__':
    logger.info('start ddp')
    logger.info('paramsQuery: %s', paramsQuery)
    logger.info('params: %s', params)
    t1=threading.Thread(target=fetchIpThread,name='fetchIpThread')
    t2=threading.Thread(target=updateDnsposThread,name='updateDnsposThread')
    t1.start()
    t2.start()
