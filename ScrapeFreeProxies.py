## python modules
from httplib import *

## local modules
from Exceptions import ProxyGrabException

## retrieves variable values from page, returning as a dictionary
def parsePortKeys(content):
    rawKeys = content\
                .split('<script type=\"text/javascript\">\n//<![CDATA[\n')[1]\
                .split('\n//]]>')[0]\
                .split(';')[0:-1]

    portKeys = {}
    for key in rawKeys:
        splitkey = key.split('=')
        name = splitkey[0].strip()
        val = splitkey[1].strip()
        intval = 0
        splitvals = val.split('^')
        for elem in splitvals:
            try:
                thisval = portKeys[elem]
            except:
                thisval = int(elem)
            intval = intval ^ thisval

        try:
            dummy = portKeys[name]
        except:
            portKeys[name] = intval

    return portKeys


## retrieves proxy addresses and port numbers from page
def parseProxies(content, portKeys):
    rawProxies = content\
                     .split('table class=\"proxytbl\" cellSpacing=\"1\">')[1]\
                     .split('</table>')[0]\
                     .split('<tr>')[1:]

    proxies = []
    for cell in rawProxies:
        ip = cell.split('<td class=\"t_ip\">')[1]\
                 .split('</td>')[0]

        portcode = cell.split('document.write(')[1]\
                       .split(');')[0]\
                       .split('^')

        port = portKeys[portcode[0]] ^ portKeys[portcode[1]] ^ int(portcode[2])

        proxy = ip + ':' + str(port)
        proxies.append(proxy)

    return proxies


## Grabs a proxy list from proxyhttp.net
## When read from the page, port numbers are encoded using variables,
## variable values are readfrom the page, and port numbers are decoded
## Proxies are written to ProxyList.raw
## Proxies are not guarenteed to work, to test use ProxyCleaner
def ScrapeFreeProxies(verbose):

    ## proxy page 1
    lookuphost = 'proxyhttp.net'
    lookupfile = '/free-list/proxy-https-security-anonymous-proxy/'
    proxyfilename = 'ProxyList.raw'

    
    connect = HTTPConnection(lookuphost,timeout=15)
    connect.request("GET", lookupfile)
    content = connect.getresponse().read()

    try:
        proxies = parseProxies(content, parsePortKeys(content))
    except:
        raise ProxyGrabException("Error scraping proxies")

    proxyfile = open(proxyfilename, 'w')
    for proxy in proxies:
        if verbose:
            print proxy
        proxyfile.write(proxy + '\n')

    ## proxy page 2
    lookupfile = '/free-list/proxy-https-security-anonymous-proxy/2'

    connect = HTTPConnection(lookuphost,timeout=15)
    connect.request("GET", lookupfile)
    content = connect.getresponse().read()

    try:
        proxies = parseProxies(content, parsePortKeys(content))
    except:
        raise ProxyGrabException("Error scraping proxies")

    for proxy in proxies:
        if verbose:
            print proxy
        proxyfile.write(proxy + '\n')
    proxyfile.close()
        

## Runs the scraper once
if __name__ == "__main__":
    ScrapeProxies(True)
