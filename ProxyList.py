## local modules
from Exceptions import ProxyGrabException
from ProxyCleaner import *
from ScrapeProxies import *

## python modules
import os
from time import sleep

####
##  ProxyList
##  @author bslawski
##    ProxyList file reader
##    Reads proxy addresses and port numbers from a given file,
##    storing with number of uses in a dictionary.  Proxies
##    returned in cycle, and are eliminated from the pool when
##    a max use count is reached or proxy is reported as faulty.
##
##  fields:
##    proxies - string list of proxy addresses and port numbers
##    nproxies - count of the elements in proxies
##    filename - ASCII file from which to read proxy addresses
##
####

class ProxyList:

    ## constructor method
    def __init__(self, proxyfile, maxcalls):
            ## list of proxy addresses as strings with int count
            self.proxies = {}
	    self.nproxies = 0
            self.proxyind = 0
            self.maxcalls = maxcalls
	    ## file to read proxy adresses from
            self.filename = proxyfile
            ## reads in proxy addresses from file
            self.populate()


    ## Cleans and opens proxy file, reading in proxy addresses,
    ## storing in the proxy list
    def populate(self):
        print '\n* populating proxy pool *'
        ## Generates and tests proxies from online source
        ## Currently handled by ProxyEngine
##        ScrapeProxies(500, False)
##        self.cleaner.clean()

        self.proxies = {}
        self.nproxies = 0
        
        try:
            proxyfile = open(self.filename, 'r')
        except IOError:
            raise ProxyGrabException(\
            "Proxy File " + self.filename + " does not exist!")		
	
        for line in proxyfile:
            proxy = line.strip()
            self.proxies[proxy] = 0

            self.nproxies += 1
			
        if self.nproxies == 0:
            sleep(30)
            self.populate()
##            raise ProxyGrabException("Proxy File is empty!")
			

    ## Retrieves and removes a proxy address from the list,
    ## returning it as a string
    def getProxy(self):
        if self.nproxies > 0:
            proxy = self.proxies.keys()[self.proxyind]
            ncalls = self.proxies[proxy]
            ncalls += 1
            self.proxies[proxy] = ncalls
            if ncalls > self.maxcalls:
                self.proxies.pop(proxy)
                self.nproxies -= 1
            self.proxyind = (self.proxyind + 1) % self.nproxies
        else:
            self.populate()
            proxy = self.getProxy()
	
        return proxy
		

    ## Eliminates a proxy reported as not working
    def reportBadProxy(self, proxy):
        try:
            self.proxies.pop(proxy)
            self.nproxies -= 1
            self.proxyind = self.proxyind % self.nproxies
        except:
            pass

		
