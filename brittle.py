import sys
import socket
import getopt
import requests
import re


## Global Variables ##
store = False
discover = False


def add_port_mapping():

    payload =   """<?xml version="1.0" encoding="utf-8"?>
                <s:Envelope>
                    <s:Body>
                        <u:AddPortMapping xmlns:u="urn:schemas-upnp-org:services:WANIPConnections:1"> 
                            <NewRemoteHost></NewRemoteHost> 
                            <NewExternalPort>1234</NewExternalPort> 
                            <NewInternalClient>192.168.1.50</NewInternalClient> 
                            <NewInternalPort>1234</NewInternalPort> 
                            <NewProtocol>TCP</NewProtocol> 
                            <NewPortMappingDescription>test</NewPortMappingDescription> 
                            <NewLeaseDuration>1000</NewLeaseDuration> 
                            <NewEnabled>1</NewEnabled> 
                        </u:AddPortMapping> 
                    </s:Body> 
                </s:Envelope>"""

    headers = { 'content-type': 'text/xml', 'SOAPAction' : 'urn:schemas-upnp-org:service:WANIPConnection:1#AddPortMapping' }
    r = requests.post('http://192.168.1.1:34753/ctl/IPConn', headers=headers, data=payload )
    print r.content
    


def store_location(data):
    #print data
    location = re.search("(?i)Location: (.+?)\r\n", data)
    if location:
        print location.group(1)



def ssdp():
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

    try:

        while 1:
            data, sokt = s.recvfrom(4096)
            if store: store_location(data)
            
    except socket.timeout:
        s.close()



def main():
    global store
    global discover



    # read the command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "dsqm", ["discover", "store", "quit", "mapping"])
    except getopt.GetoptError as err:
        print str(err)
        sys.exit(-1)

    for o, a in opts:
        if o in ("-d", "--discover"):
            discover = True
        elif o in ("-s", "--store"):
            store = True
        elif o in ("-q", "--quit"):
            sys.exit(0)
        elif o in ("-m", "--mapping"):
            add_port_mapping()
        else:
            assert False, "Unhandled Option"

    if discover:
        ssdp()

if __name__ == "__main__":
    main()
