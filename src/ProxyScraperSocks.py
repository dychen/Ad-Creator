import httplib
import re
import socks
import socket
import urllib2
from multiprocessing import Process, Queue
import multiprocessing

def call_proxy_list_site(url, connection):
    connection.request('GET', url)
    return connection.getresponse().read()

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
    protocol = contents.split(address)[1].split('<td class="t_type">')[1].split('</td>')[0].strip()
    if protocol == '4':
        return 'socks4'
    else:
        return 'socks5'

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
    ip = proxy.split(':')[0]
    port = int(proxy.split(':')[1])
    if protocol == 'socks4':
        protocol = socks.PROXY_TYPE_SOCKS4
    else:
        protocol = socks.PROXY_TYPE_SOCKS5

    try:
        socks.setdefaultproxy(protocol, ip, port)
        socket.socket = socks.socksocket
        response = urllib2.urlopen(test_url, timeout = 60)
        html = json.loads(response.read())
        if html['remaining_hits'] > 0:
            print 'Accepted'
            return True
        else:
            print 'Not enough calls remaining.'
            return False
    except Exception, e:
        return False
    return False

def worker_proxy_check(input, output):
    next_proxy = input.get()
    proxy = next_proxy[0]
    protocol = next_proxy[1]
    if check_proxy(proxy, protocol):
        output.put((proxy, protocol))

if __name__ == '__main__':
    proxies = {}
    jobs = []

    server = 'sockslist.net'
    url_list = ['/proxy/server-socks-hide-ip-address',
                '/proxy/server-socks-hide-ip-address/2#proxylist',
                '/proxy/server-socks-hide-ip-address/3#proxylist']

    connection = httplib.HTTPConnection(server)
    for url in url_list:
        contents = call_proxy_list_site(url, connection)
        port_codes = make_code_dictionary(contents)
        proxies.update(parse_proxy_list(contents, port_codes))

    unchecked_proxies = Queue()
    checked_proxies = Queue()
    for (proxy, protocol) in proxies.items():
        unchecked_proxies.put((proxy, protocol))

    procs = []
    for proxy, protocol in proxies.items():
        p = Process(target = worker_proxy_check, args = (unchecked_proxies, checked_proxies))
        procs.append(p)
        p.start()

    print "Waiting for workers to finish..."
    for proc in procs:
        proc.join()

    clean_proxies = {}
    while not checked_proxies.empty():
        result = checked_proxies.get()
        proxy = result[0]
        protocol = result[1]
        clean_proxies[proxy] = protocol

    print proxies
    print len(proxies)
    print clean_proxies
    print len(clean_proxies)
