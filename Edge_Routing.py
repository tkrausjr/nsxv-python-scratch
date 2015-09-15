'''
Created on Oct 7, 2013

@author: tkraus
'''
global creds
global switches 
global vwires
global edge_id
global headers

nsx_ip="10.148.169.16"
nsx_port = 443
username = "admin"
password = "VMware1!"
datacenter_id =  'datacenter-2'
vdr_edge_id = 'edge-105'
svc_edge_id = 'edge-104'

import base64
import urllib2
import httplib2
import httplib
from xml.dom.minidom import parseString
from xml.dom.minidom import parse
import xml.etree.ElementTree as ET

creds= base64.urlsafe_b64encode(username + ':' + password)
headers = {'Content-Type' : 'application/xml','Authorization' : 'Basic ' + creds }

def config_vdr(edge_id,gw,router_id,vnic,proto_add,forward_add):
    xml_string = '<routing><routingGlobalConfig><routerId>'+router_id+'</routerId><logging><enable>false</enable><logLevel>info</logLevel></logging></routingGlobalConfig><staticRouting><defaultRoute><description>defaultRoute</description><vnic>'+vnic+'</vnic><gatewayAddress>'+gw+'</gatewayAddress><mtu>1500</mtu></defaultRoute></staticRouting><ospf><enabled>true</enabled><forwardingAddress>'+forward_add+'</forwardingAddress><protocolAddress>' +proto_add+ '</protocolAddress><ospfAreas><ospfArea><areaId>100</areaId><type>normal</type></ospfArea></ospfAreas><ospfInterfaces><ospfInterface><vnic>'+vnic+'</vnic><areaId>100</areaId><helloInterval>10</helloInterval><deadInterval>40</deadInterval><priority>128</priority><cost>10</cost></ospfInterface></ospfInterfaces><redistribution><enabled>true</enabled><rules><rule><from><ospf>true</ospf> <connected>true</connected></from><action>permit</action></rule></rules></redistribution></ospf></routing>'
    conn = httplib.HTTPSConnection(nsx_ip, nsx_port)
    conn.request('PUT', 'https://' + nsx_ip + '/api/4.0/edges/' + edge_id+'/routing/config',xml_string,headers)
    response = conn.getresponse()
    print response.status
    
    #if response.status != 201:
            #print response.status
            #print "VDR Not created..."
            #exit(1)
    #else:
            #location = response.getheader('location', default=None)
            #print location
            #split = location.split('/')
            #edge_id = split[-1]
            #print str(edge_id) + " Created"
            #return edge_id

def get_edges():
    url='https://' + nsx_ip + '/api/4.0/edges'
    req = urllib2.Request(url=url,  
        headers=headers)
    response=urllib2.urlopen(req)
    data=response.read()
    xmldoc=ET.fromstring(data)
    edges=xmldoc.findall("./edgePage/edgeSummary/objectId")
    return edges
    
def main():
    edges=get_edges()
    for edge in edges:
        edge_id = edge.text
        print edge_id
    
    # Configure VDR Edge
    gw = '192.168.10.1'
    router_id = '192.168.10.2'
    vnic = '2'
    proto_add = '192.168.10.3'
    forward_add = '192.168.10.2'
    config_vdr(vdr_edge_id,gw,router_id,vnic,proto_add,forward_add)
     
main()





   



