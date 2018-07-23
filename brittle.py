import sys
import socket
import getopt
import requests
import re

## Global Variables ##
store = False
discover = False


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
        opts, args = getopt.getopt(sys.argv[1:], "ds", ["discover", "store"])
    except getopt.GetoptError as err:
        print str(err)
        sys.exit(-1)

    for o, a in opts:
        if o in ("-d", "--discover"):
            discover = True
        elif o in ("-s", "--store"):
            store = True
        else:
            assert False, "Unhandled Option"

    if discover:
        ssdp()

if __name__ == "__main__":
    main()
