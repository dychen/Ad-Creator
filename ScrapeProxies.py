## python modules
from httplib import *
from random import *

## local modules
from Exceptions import ProxyGrabException

## Grabs a VIP proxy list from freeproxylist.org (requires monthly subscription)
## Proxies are written to ProxyList.raw
## Proxies are not guarenteed to work, to test use ProxyCleaner
def ScrapeProxies(maxproxies, verbose):
    ## VIP key
    lookuphost = 'freeproxylist.org'
    lookupfile = '/en/downloader.php?key=tDWxidHced7DDEhlIYyMtCqDZKuc3jPf&filter=any|any|any|2|any|any|0|0|15.0000|0|360'
    ## savefile for retrieved proxies
    proxyfilename = 'ProxyList.raw'

    try:    
        connect = HTTPConnection(lookuphost,timeout=15)
        connect.request("GET", lookupfile)
        content = connect.getresponse().read()
    except:
        raise ProxyGrabException("Unable to retrieve paid proxy list")


##    print content
    proxyfile = open(proxyfilename, 'w')
    nproxies = 0
    splitcontent = content.split('\n')
    navailable = len(splitcontent)
    while navailable > 0 and nproxies < maxproxies:
        line = splitcontent.pop(int(random() * navailable))
        if verbose:
            print line
        proxyfile.write(line + '\n')
        nproxies += 1
        navailable -= 1

    proxyfile.close()
        

## Runs the scraper once for 500 proxies
if __name__ == "__main__":
    ScrapeProxies(500, True)
