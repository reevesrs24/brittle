import socket


def discover():
    ### UPnP Architecture Specs ###
    # M-SEARCH - Method for search requests
    # HOST - Multicast channed and port reserved for SSDP
    # MAN - Required by HTTP Exension Framework, defines the scope (namespace) of the extension
    # MX - MAximum wait time in seconds
    # ST: Required search target, pre defined values
    SSDP = 'M-SEARCH * HTTP/1.1\r\n' \
            'HOST:239.255.255.250:1900\r\n' \
            'MAN:"ssdp:discover"\r\n' \
            'MX:5\r\n' \
            'ST:upnp:rootdevice\r\n' \
            '\r\n'


    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(5)
    s.sendto(SSDP, ('239.255.255.250', 1900) )
    try:

        while 1:
            data, sokt = s.recvfrom(4096)
            if not data: break
            print sokt
            print data
    except socket.timeout:
        s.close()



def main():
    discover()


if __name__ == "__main__":
    main()