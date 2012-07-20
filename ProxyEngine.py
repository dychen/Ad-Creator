## local modules
from ScrapeProxies import *
from ScrapeFreeProxies import *
from ProxyCleaner import *
from Exceptions import ProxyGrabException

## python modules
from time import sleep


####
##  ProxyEngine
##  @author bslawski
##    Continuously scrapes proxies from the internet,
##    testing them and writing working proxies to file.
##    Should be running while tweet harvesting programs
##    are running in order to keep proxy lists fresh.
##
####

def ProxyEngine(cleaner):
    try:
##        ScrapeProxies(800, False)
        ScrapeFreeProxies(False)
    except ProxyGrabException:
        pass
 
    cleaner.clean()


if __name__ == "__main__":
    ## start with a clean file
    try:
        os.remove('ProxyList.dat')
    except:
        pass

    ## loop forever, pausing between loops
    cleaner = ProxyCleaner(7., False)
    while(True):
        ProxyEngine(cleaner)
        sleep(30)
