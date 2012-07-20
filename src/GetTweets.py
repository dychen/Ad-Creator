import urllib2
import json

def write_results_to_file(results):
    filename = 'tweets'
    extension = '.txt'
    f = open(filename + extension, 'w')
    for key in results:
        f.write(key + ': ' + results[key] + '\n')
    f.close()

base_url = 'http://search.twitter.com/search.json?q='
query = 'coke'
additional_params = '&lang=en&rpp=100&page=1'
response = urllib2.urlopen(base_url + query + additional_params)
html = json.loads(response.read())
results = {}

for tweet in html['results']:
    results[tweet['from_user_id_str']] = tweet['text'].encode('ascii', 'replace')

print results
print len(results)
write_results_to_file(results)


