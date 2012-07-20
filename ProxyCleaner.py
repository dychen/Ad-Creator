## python modules
from time import *
import eventlet
from eventlet.green.httplib import *
from sets import *
from shutil import *

## local modules
from FileWriter import *


####
##  ProxyCleaner
##  @author bslawski
##    Reads proxy address data downloaded from the internet,
##    ripping the first object in each line as a proxy address
##    and port number in the format:
##        ##.##.##.##:####
##    Tests proxy addresses for remaining Twitter API calls
##    in the hour, writing only those with calls remaining
##    to the proxy list file.
##
##    in file - ProxyList.raw
##    out file - ProxyList.dat
##
####

class ProxyCleaner:

    ## constructor method
    def __init__(self, timeout, verbose):
        ## higher number results in more selective proxy latency requirements
        self.TIMEOUT_LATENCY = 2.0
        ## higher number results in more responsive timeout adjustment
        ## 0 turns off adaptive timeouts
        self.TIMEOUT_ADJ = .05
        ## the adjustable timeout will not get larger than this value
        self.MAX_TIMEOUT = 20.

        ## initial timeout length
        self.timeout = timeout
        ## prints runtime info iff True
        self.verbose = verbose

        self.lookup = 'http://api.twitter.com/1/account/rate_limit_status.json'


    ## reads the proxies in ProxyList.raw,
    ## testing and writing working proxies to ProxyList.dat
    def clean(self):
        newproxies = []

        infile = open('ProxyList.raw', 'r')
        outfile = FileWriter('ProxyList', 100, False)

        unused = 0
        toTest = []

        latencies = {}

        ## reads proxies from raw file
        for line in infile:
            ## proxy address is the first item in the row
            try:
                proxy = ((line.split())[0]).strip()
                toTest.append(proxy)
            except IndexError:
                infile.close()
                outfile.close()
                print 'no proxies'
                return

        toTest = list(set(toTest))
        ntested = len(toTest)

        ## multi-threaded calls to twitter api rate limit api page
        pool = eventlet.GreenPool()
        starttime = clock()
        for proxytuple in pool.imap(self.fetch, toTest):
            if proxytuple == '':
                continue

            proxydata, proxy = proxytuple

            try:
                proxydata = (((((proxydata.split('\"remaining_hits\":'))[1])
                                   .split(','))[0]).split('}'))[0]
            except:
                if self.verbose:
                    print '\t', proxy + ' parse error, removing'
                continue


            ## writes proxy iff successful lookup and > 50 API calls remaining
            if int(proxydata) > 50:
                newproxies.append(proxy)
                self.timeout -= self.TIMEOUT_ADJ
                if self.verbose:
                    print '\t', proxy + ' has ' + proxydata + ' hits'
                latencies[clock() - starttime] = proxy
            else:
                if self.verbose:
                    print '\t', proxy + ' is spent, removing'

        ## writes best 250 working proxies to file
        times = latencies.keys()
        times.sort()
        if len(times) > 250:
            bestTimes = times[0:250]
        else:
            bestTimes = times
        newproxies = []
        for thisTime in bestTimes:
            newproxies.append(latencies[thisTime])
        unused = len(newproxies)
        for proxy in newproxies:
            outfile.write(proxy + '\n')

        infile.close()
        outfile.close()

##        if self.verbose:
        print 'proxies: ', unused, 'timeout: ', self.timeout

##        print 'proxies: ', unused, ' / ' , ntested, \
##              '  latency range: ', [bestTimes[0], bestTimes[-1]]


    ## attempts to fetch api info page, 
    ## adjusting timeout length for fail lookups
    def fetch(self, proxy):
        ## looks up rate limit data using proxy
        try:
            connect = HTTPConnection(proxy, timeout=self.timeout)
            connect.request("GET", self.lookup)
            proxydata = connect.getresponse().read()
            return proxydata, proxy
        except:
            self.timeout += self.TIMEOUT_ADJ / (self.timeout * self.TIMEOUT_LATENCY)
            if self.timeout > self.MAX_TIMEOUT:
                self.timeout = self.MAX_TIMEOUT
            if self.verbose:
                print '\t', proxy + ' lookup error, removing'
            return ''
        


## Test
## Runs the cleaner once
if __name__ == "__main__":
    testCleaner = ProxyCleaner(7., True)
    testCleaner.clean()
