'''
Created on Oct 2, 2013

@author: tkraus
'''
global creds
global switches 
global vwires
global edge_id

nsx_ip="192.168.20.111"
nsx_port = 443
username = "admin"
password = "vmware"
switches = ['Web-Tier','App-Tier'] 
edge_id =  'edge-10'

import base64
import urllib2
from xml.dom.minidom import parseString
from xml.dom import minidom
from xml import dom
import xml.etree.ElementTree as ET
from xml import etree

creds= base64.urlsafe_b64encode(username + ':' + password)

def nsx_hello():
    h=httplib2.Http(disable_ssl_certificate_validation=True)
    #h.add_credentials(username,password)
    resp, content = h.request("https://192.168.20.111/api/versions", 'GET', headers = {'Authorization' : 'Basic ' + creds})
    print content
    print resp


def get_ls():
    url='https://' + nsx_ip + '/api/2.0/vdn/scopes/vdnscope-1/virtualwires'
    req = urllib2.Request(url=url,  
        headers={'Content-Type': 'application/xml','Authorization' : 'Basic ' + creds})
    response=urllib2.urlopen(req)
    data=response.read()
    xmldoc=parseString(data)
    for vwire in xmldoc.getElementsByTagName('objectId'):
        print vwire.toxml()

def main():
    nsx_hello()
    vwires=get_ls()
    print vwires
 
main()