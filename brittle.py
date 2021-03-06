#!/usr/bin/env python

import sys
import socket
import getopt
import requests
import re
import xml.etree.ElementTree as ET

## Global Variables ##
store = False
discover = False
url = 'http://192.168.1.1:5431/control/WANIPConnection'

def get_generic_port_mapping_entry():
    
    payload =   """<?xml version="1.0" encoding="utf-8"?>
                <s:Envelope>
                    <s:Body>
                        <u:GetGenericPortMappingEntry xmlns:u="urn:schemas-upnp-org:services:WANIPConnections:1"> 
                           <NewPortMappingIndex></NewPortMappingIndex> 
                        </u:GetGenericPortMappingEntry> 
                    </s:Body> 
                </s:Envelope>"""

    headers = { 'content-type': 'text/xml', 'SOAPAction' : 'urn:schemas-upnp-org:service:WANIPConnection:1#GetGenericPortMappingEntry' }
    r = requests.post( url, headers=headers, data=payload )
    print r.content


def get_status_info():

    payload =   """<?xml version="1.0" encoding="utf-8"?>
                <s:Envelope>
                    <s:Body>
                        <u:GetStatusInfo xmlns:u="urn:schemas-upnp-org:services:WANIPConnections:1"> 
                           <NewConnectionStatus></NewConnectionStatus> 
                           <NewLastConnectionError></NewLastConnectionError>
                           <NewUptime></NewUptime>  
                        </u:GetStatusInfo> 
                    </s:Body> 
                </s:Envelope>"""

    headers = { 'content-type': 'text/xml', 'SOAPAction' : 'urn:schemas-upnp-org:service:WANIPConnection:1#GetStatusInfo' }
    r = requests.post( url, headers=headers, data=payload )
    print r.content

def remove_port_mapping():

    payload =   """<?xml version="1.0" encoding="utf-8"?>
                <s:Envelope>
                    <s:Body>
                        <u:DeletePortMapping xmlns:u="urn:schemas-upnp-org:services:WANIPConnections:1"> 
                           <NewRemoteHost></NewRemoteHost> 
                           <NewExternalPort>;reboot</NewExternalPort>
                           <NewProtocol>TCP</NewProtocol>  
                        </u:DeletePortMapping> 
                    </s:Body> 
                </s:Envelope>"""

    headers = { 'content-type': 'text/xml', 'SOAPAction' : 'urn:schemas-upnp-org:service:WANIPConnection:1#DeletePortMapping' }
    r = requests.post( url, headers=headers, data=payload )
    print r.content


def get_external_ip_addr():

    payload =   """<?xml version="1.0" encoding="utf-8"?>
                <s:Envelope>
                    <s:Body>
                        <u:GetExternalIPAddress xmlns:u="urn:schemas-upnp-org:services:WANIPConnections:1"> 
                            <NewExternalIPAddress></NewExternalIPAddress>  
                        </u:GetExternalIPAddress> 
                    </s:Body> 
                </s:Envelope>"""

    headers = { 'content-type': 'text/xml', 'SOAPAction' : 'urn:schemas-upnp-org:service:WANIPConnection:1#GetExternalIPAddress' }
    r = requests.post( url, headers=headers, data=payload )
    print r.content


def add_port_mapping():

    payload =   """<?xml version="1.0" encoding="utf-8"?>
                <s:Envelope>
                    <s:Body>
                        <u:AddPortMapping xmlns:u="urn:schemas-upnp-org:services:WANIPConnections:1"> 
                            <NewRemoteHost></NewRemoteHost> 
                            <NewExternalPort>7777</NewExternalPort> 
                            <NewInternalClient>192.168.1.50</NewInternalClient> 
                            <NewInternalPort>80</NewInternalPort> 
                            <NewProtocol>TCP</NewProtocol> 
                            <NewPortMappingDescription></NewPortMappingDescription> 
                            <NewLeaseDuration>0</NewLeaseDuration> 
                            <NewEnabled>1</NewEnabled> 
                        </u:AddPortMapping> 
                    </s:Body> 
                </s:Envelope>"""

    headers = { 'content-type': 'text/xml', 'SOAPAction' : 'urn:schemas-upnp-org:service:WANIPConnection:1#AddPortMapping' }
    r = requests.post( url, headers=headers, data=payload )
    print r.content
    

def set_services(location):
    print "Setting Service to {0}".format(location)
    r = requests.get( location )
    #print r.content
    tree = ET.fromstring( r.content )
     
    

def set_location(url_locations):

    for i in range(len(url_locations)):
        print "[{0}] {1}".format(i, url_locations[i])
    idx = int ( input("Set Location: ") )
    
    if idx > 0 and idx < len(url_locations):
        set_services(url_locations[idx])
    else:
        print "Error!"
        sys.exit(0)
    



def store_location(data):
    #print data
    location = re.search("(?i)Location: (.+?)\r\n", data)
    if location:
        return location.group(1)



def ssdp():

    url_locations = []

    ### UPnP Architecture Specs ###
    # M-SEARCH - Method for search requests
    # HOST - Multicast channed and port reserved for SSDP
    # MAN - Required by HTTP Exension Framework, defines the scope (namespace) of the extension
    # MX - MAximum wait time in seconds
    # ST: Required search target, pre defined values
    SSDP =  ('M-SEARCH * HTTP/1.1\r\n' 
            'HOST:239.255.255.250:1900\r\n' 
            'MAN:"ssdp:discover"\r\n' 
            'MX:10\r\n' 
            'ST:upnp:rootdevice\r\n'
            '\r\n')


    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(5)
    s.sendto(SSDP, ('239.255.255.250', 1900) )
    
    

    print "Discovering..."

    try:

        while 1:
            data, sokt = s.recvfrom(4096)
            url_locations.append( store_location(data) )
            
    except socket.timeout:
        s.close()
    
    if store and len(url_locations) > 0:
        set_location(url_locations)
    elif store:
        print "Nothing Found!"



def main():
    global store
    global discover



    # read the command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "dsqmersg", ["discover", "set", "quit", "mapping", "external", "remove", "status", "generic"])
    except getopt.GetoptError as err:
        print str(err)
        sys.exit(-1)

    for o, a in opts:
        if o in ("-d", "--discover"):
            discover = True
        elif o in ("-s", "--set"):
            store = True
        elif o in ("-q", "--quit"):
            sys.exit(0)
        elif o in ("-m", "--mapping"):
            add_port_mapping()
        elif o in ("-e", "--external"):
            get_external_ip_addr()
        elif o in ("-r", "--remove"):
            remove_port_mapping()
        elif o in ("-s", "--status"):
            get_status_info()
        elif o in ("-g", "--generic"):
            get_generic_port_mapping_entry()
        else:
            assert False, "Unhandled Option"

    if discover:
        ssdp()

if __name__ == "__main__":
    main()
