import httplib
import re
import urllib2
from multiprocessing import Process, Queue

def call_proxy_list_site(url):
    connect.request('GET', url)
    return connect.getresponse().read()

def make_code_dictionary(contents):
    code = contents.split('//<![CDATA[')[1].split('//]]>')[0].strip()[:-1]
    decoder = {}
    for entry in code.split(';'):
        key = entry.split('=')[0].strip()
        value = entry.split('=')[1].strip()
        expression = []
        for element in value.split('^'):
            if element in decoder.keys():
                expression.append(int(decoder[element]))
            else:
                expression.append(int(element))
        decoder[key] = str(reduce(lambda x, y: x^y, expression))
    return decoder

def parse_proxies(contents):
    return list(set(re.findall('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', contents)))

def decode_port(contents, coded_port, port_codes):
    expression = []
    for element in coded_port.split('^'):
        if element in port_codes.keys():
            expression.append(int(port_codes[element]))
        else:
            expression.append(int(element))
    return str(reduce(lambda x, y: x^y, expression))

def parse_protocol(contents, address):
    protocol = contents.split(address)[1].split('<td class="t_https">')[1].split('</td>')[0]
    if protocol == '-':
        return 'http'
    else:
        return 'https'

def parse_ports(contents, proxy_list, port_codes):
    proxies = {}
    for address in proxy_list:
        coded_port = contents.split(address)[1].split('document.write(')[1].split(')')[0]
        proxy = address + ':' +  decode_port(contents, coded_port, port_codes)
        proxies[proxy] = parse_protocol(contents, address)
    return proxies

def parse_proxy_list(contents, port_codes):
    proxy_list = parse_proxies(contents)
    return parse_ports(contents, proxy_list, port_codes)

def check_proxy(proxy, protocol):
    print proxy + ': ' + protocol
    test_url = 'http://api.twitter.com/1/account/rate_limit_status.json'
    proxies = {protocol: proxy}
    proxy = urllib2.ProxyHandler(proxies)
    opener = urllib2.build_opener(proxy)
    urllib2.install_opener(opener)
    try:
        response = urllib2.urlopen(test_url)
        html = json.loads(response.read())
        if html['remaining_hits'] > 0:
           print 'Accepted'
           return True
        return False
    except:
        return False
    return False

if __name__ == '__main__':
    proxies = {}
    jobs = []

    server = 'proxyhttp.net'
    url_list = ['/free-list/anonymous-server-hide-ip-address/',
                '/free-list/anonymous-server-hide-ip-address/2#proxylist',
                '/free-list/anonymous-server-hide-ip-address/3#proxylist',
                '/free-list/anonymous-server-hide-ip-address/4#proxylist',
                '/free-list/anonymous-server-hide-ip-address/5#proxylist',
                '/free-list/anonymous-server-hide-ip-address/6#proxylist',
                '/free-list/anonymous-server-hide-ip-address/7#proxylist',
                '/free-list/anonymous-server-hide-ip-address/8#proxylist',
                '/free-list/anonymous-server-hide-ip-address/9#proxylist']

    connect = httplib.HTTPConnection(server)
    for url in url_list:
        contents = call_proxy_list_site(url)
        port_codes = make_code_dictionary(contents)
        proxies.update(parse_proxy_list(contents, port_codes))

    clean_proxies = {}
    for proxy, protocol in proxies.items():
        p = Process(target = clean_proxy, args = (proxy, protocol))
        jobs.append(p)
        p.start()
        if check_proxy(proxy, protocol):
            clean_proxies[proxy] = protocol

    print proxies
    print len(proxies)
    print clean_proxies
    print len(clean_proxies)
