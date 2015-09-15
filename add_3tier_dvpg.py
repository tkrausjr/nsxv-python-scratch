'''
Created on Oct 2, 2013

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
internal_switches = ['Web-Tier-LS','App-Tier-LS','DB-Tier-LS'] 
uplink_switch = 'Transport-Network-01' 
tz_name = 'TZ1'
datacenter_id =  'datacenter-2'
vdr_edge_name = 'VDR-01'
svc_edge_name = 'SVC-Edge-01'

import base64
import urllib2
import httplib
from xml.dom.minidom import parseString
import xml.etree.ElementTree as ET

creds= base64.urlsafe_b64encode(username + ':' + password)
headers = {'Content-Type' : 'application/xml','Authorization' : 'Basic ' + creds }

def create_tz(tz_name):
    url='https://' + nsx_ip + '/api/2.0/vdn/scopes'
    xml_string ='<vdnScope><name>TZ1</name><objectId></objectId><clusters><cluster><cluster><objectId>domain-c7</objectId></cluster></cluster><cluster><cluster><objectId>domain-c25</objectId></cluster></cluster><cluster><cluster><objectId>domain-c27</objectId></cluster></cluster></clusters></vdnScope>'
    req=urllib2.Request(url=url,    
        data=xml_string, 
        headers={'Content-Type': 'application/xml','Authorization' : 'Basic ' + creds})
    response=urllib2.urlopen(req)
    tz_id=response.read()
    return tz_id

def create_ls(ls_name):
    url='https://' + nsx_ip + '/api/2.0/vdn/scopes/vdnscope-4/virtualwires'
    xml_string ='<virtualWireCreateSpec><name>' + ls_name + '</name><description>Created via REST API</description><tenantId>virtual wire tenant</tenantId><controlPlaneMode>UNICAST_MODE</controlPlaneMode></virtualWireCreateSpec>'
    req = urllib2.Request(url=url, 
        data=xml_string, 
        headers={'Content-Type': 'application/xml','Authorization' : 'Basic ' + creds})
    response=urllib2.urlopen(req)
    vwire_id=response.read()
    return vwire_id

def create_edge(edge_name,edge_type):
    xml_string ='<edge><datacenterMoid>' + datacenter_id + '</datacenterMoid><type>distributedRouter</type><appliances><appliance><resourcePoolId>domain-c7</resourcePoolId><datastoreId>datastore-11</datastoreId><vmHostname>' + edge_name + '</vmHostname></appliance></appliances><mgmtInterface><connectedToId>dvportgroup-21</connectedToId></mgmtInterface></edge>'
    conn = httplib.HTTPSConnection(nsx_ip, nsx_port)
    conn.request('POST', 'https://' + nsx_ip + '/api/4.0/edges',xml_string,headers)
    response = conn.getresponse()
    location = response.getheader('location', default=None)
    
    if response.status != 201:
            print response.status
            print response.read()
            print "VDR Not created..."
            exit(1)
    else:
            location = response.getheader('location', default=None)
            split = location.split('/')
            edge_id = split[-1]
            print edge_id
            print "VDR Created Successfully"
            return edge_id
        
def create_svc_edge(svc_edge_name,dvpg,int_ip,int_mask,int_type):
    xml_string ='<edge><datacenterMoid>'+datacenter_id+'</datacenterMoid><name>'+svc_edge_name+'</name><appliances><appliance><resourcePoolId>domain-c7</resourcePoolId><datastoreId>datastore-11</datastoreId></appliance></appliances><vnics><vnic><index>0</index><type>'+int_type+'</type><isConnected>true</isConnected><portgroupId>'+dvpg+'</portgroupId><addressGroups><addressGroup><primaryAddress>'+int_ip+'</primaryAddress><subnetMask>'+int_mask+'</subnetMask></addressGroup></addressGroups></vnic></vnics></edge>'
    # Needed to do unnatural things because NSX returning the Edge ID as a URI value in a Response Header. NICE
    conn = httplib.HTTPSConnection(nsx_ip, nsx_port)
    conn.request('POST', 'https://' + nsx_ip + '/api/3.0/edges',xml_string,headers)
    response = conn.getresponse()
    location = response.getheader('location', default=None)
    
    if response.status != 201:
            print response.status
            print "Services Edge Not created..."
            exit(1)
    else:
            location = response.getheader('location', default=None)
            split = location.split('/')
            svc_edge_id = split[-1]
            print svc_edge_id
            print "Services Edge Created Successfully"
            return svc_edge_id

def connect_ls(edge_id,vwire_name,vwire_id,int_ip,int_mask,int_type):
    print str(vwire_id) +' : ' + str(int_ip) + ' : ' + str(int_type)
    url='https://' + nsx_ip + '/api/4.0/edges/' + edge_id + '/interfaces/?action=patch'
    xml_string ='<interfaces><interface><name>' + vwire_name + '</name><addressGroups><addressGroup><primaryAddress>' + int_ip + '</primaryAddress><subnetMask>'+int_mask+'</subnetMask></addressGroup></addressGroups><mtu>1500</mtu><type>' + int_type + '</type><isConnected>true</isConnected><connectedToId>' + vwire_id + '</connectedToId></interface></interfaces>'
    req = urllib2.Request(url=url, 
        data=xml_string, 
        headers={'Content-Type': 'application/xml','Authorization' : 'Basic ' + creds})
    response=urllib2.urlopen(req)
   
def connect_svc_ls(edge_id,vwire_name,vwire_id,int_ip,int_mask,int_type,int_index):
    print str(vwire_id) +' : ' + str(int_ip) + ' : ' + str(int_type)
    url='https://' + nsx_ip + '/api/3.0/edges/' + edge_id + '/vnics/?action=patch'
    xml_string ='<vnics><vnic><index>'+ int_index +'"</index><name>' + vwire_name + '</name><addressGroups><addressGroup><primaryAddress>' + int_ip + '</primaryAddress><subnetMask>'+int_mask+'</subnetMask></addressGroup></addressGroups><mtu>1500</mtu><type>' + int_type + '</type><isConnected>true</isConnected><portgroupId>' + vwire_id + '</portgroupId></vnic></vnics>'
    req = urllib2.Request(url=url, 
        data=xml_string, 
        headers={'Content-Type': 'application/xml','Authorization' : 'Basic ' + creds})
    response=urllib2.urlopen(req)

def main():
    vwires = [];
    print " Creating Logical Switches..."
    for i in internal_switches:
        vwire_id = create_ls(i)
        vwires.append(vwire_id)
    print "----The following Logical Switches were created:  " + str(vwires)
    # Create a VDR
    print " Creating Distributed Logical Router... "
    edge_type = 'distributedRouter'
    vdr_edge_id = create_edge(vdr_edge_name, edge_type)
    print vdr_edge_id
    
    # Create a Services Edge
    dvpg = 'dvportgroup-20'
    int_ip = '192.168.100.6'
    int_mask = '255.255.255.0'
    int_type = 'uplink'
    svc_edge_id = create_svc_edge(svc_edge_name,dvpg,int_ip,int_mask,int_type)
    print svc_edge_id
    # Create LIFS on VDR create above
    # loop through returned rows of virtual-wires and append virtualwire ID to
    x=10
    print " Creating and configuring VDR Interfaces or LIFs..."
    for index, ls_id in enumerate(vwires):  
        xstring = str(x)
        x+= 10
        int_ip = '172.16.' + xstring + '.1'
        int_mask='255.255.255.0'
        int_type = 'internal'
        name = ls_id +'-API'
        int_lif = connect_ls(vdr_edge_id,name,ls_id,int_ip,int_mask,int_type)
    
    # Create Transport LS and Uplinks LIF on VDR
    print "Creating and configuring Transport LS Interface on " + str(vdr_edge_id) + ' Distributed Logical Router'
    int_ip = '192.168.11.2'
    int_mask ='255.255.255.0'
    int_type = 'uplink'
    transport_net_id = 'dvportgroup-336'
    name=transport_net_id + '-API'
    uplk_lif = connect_ls(vdr_edge_id,name,transport_net_id,int_ip,int_mask,int_type)
    print "Done. Transport LS Interface configured on " + str(vdr_edge_id)
    
    # Create LIF on Services Edge
    print "Creating and configuring Transport LS Interface on " + str(svc_edge_id) + ' Services Edge GW'
    int_ip = '192.168.11.1'
    int_mask ='255.255.255.0'
    int_type = 'internal'
    int_index='1'
    uplk_lif = connect_svc_ls(svc_edge_id,name,transport_net_id,int_ip,int_mask,int_type,int_index)
    print "Done. Transport LS Interface configured on " + str(svc_edge_id) + ' Services Edge GW'
    
    tz_id = create_tz(tz_name)
    print tz_id
    
    
main()


