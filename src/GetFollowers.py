import urllib2
import psycopg2
import json
import itertools

def write_results_to_file(filename, results, num_followers):
    extension = '.txt'
    f = open(filename + extension, 'w')
    f.write(str(num_followers) + '\n')
    for key in results:
        f.write(str(key) + ': ' + str(results[key]) + '\n')
    f.close()

# Sends a GET request to twitter
# Input:
# url string of the url you want to hit
# params string or tuple of the parameters you want to pass to the url
# e.g. user_id, cursor
# Output:
# dictionary containing the parsed JSON response
def call_twitter(url, params):
    try:
        response = urllib2.urlopen(url % params)
    except urllib2.HTTPError, e:
        print 'Error: ' str(e.code)
        break
    return json.loads(response.read())

# Returns the user_ids of all followers of a specific user
# Input:
# id integer id of the user you want to find the followers of
# Output:
# array containing the list of user_ids of all followers for that user
def get_followers(id):
    followers = []
    base_url = 'http://api.twitter.com/1/followers/ids.json?&user_id=%s&cursor=%s'
    cursor = -1
    while (cursor != 0):
        try:
            response = urllib2.urlopen(base_url % (id, cursor))
        except urllib2.HTTPError, e:
            print 'Error: ' + str(e.code)
            break
        html = json.loads(response.read())
        followers.append(html['ids'])
        cursor = html['next_cursor']
    return list(itertools.chain(*followers))

# Returns the user_ids of all friends of a specific user
# Input:
# user string of the user you want to find friends of
# Output:
# array containing the list of user_ids of all followers for that user
def get_friends(id):
    friends = []
    base_url = 'http://api.twitter.com/1/friends/ids.json?&user_id=%s&cursor=%s'
    cursor = -1
    while (cursor != 0):
        try:
            response = urllib2.urlopen(base_url % (id, cursor))
        except urllib2.HTTPError, e:
            print 'Error: ' + str(e.code) 
            break
        html = json.loads(response.read())
        friends.append(html['ids'])
        cursor = html['next_cursor']
    return list(itertools.chain(*friends))

# Returns a followers dictionary with each follower and all of his friends
# Input:
# follower_ids array of follower ids
# Output:
# dictionary of (follower_id: list of that follower's friends)
def create_followers_dict(follower_ids):
    followers = {}
    for follower_id in follower_ids:
        print 'create_followers_dict follower_id: ' + str(follower_id)
        follower_friends = get_friends(follower_id)
        if len(follower_friends) != 0: 
            followers[follower_id] = follower_friends 
    return followers

# Updates the counts in the friends dictionary
# Input:
# friends dictionary of (friend: count of number of followers with that friend)
# followers dictionary of (follower_id: list of that follower's friends)
# Output:
# updated friends dictionary
def update_friends_dict(friends, followers):
    for follower in followers:
        for friend in followers[follower]:
            if friend not in friends:
                friends[friend] = 1
            else:
                friends[friend] += 1

# Gets the twitter id for a given twitter handle
# Input:
# handle string of the twitter user's screen name
# Output:
# integer id corresponding to the handle
def get_id(handle):
    base_url = 'https://api.twitter.com/1/users/lookup.json?screen_name=%s'
    try:
        response = urllib2.urlopen(base_url % handle)
    except urllib2.HTTPError, e:
        print 'Error: ' + str(e.code)
        return 
    html = json.loads(response.read())
    return html[0]['id']

# Gets the twitter handle for a given twitter id
# Input:
# handle string of the twitter user's id
# Output:
# string handle corresponding to the id
def get_screen_name(id):
    base_url = 'https://api.twitter.com/1/users/lookup.json?user_id=%s'
    try:
        response = urllib2.urlopen(base_url % id)
    except urllib2.HTTPError, e:
        print 'Error: ' + str(e.code)
        return
    html = json.loads(response.read())
    return html[0]['screen_name']

# Calculates the correlations between the target brand and all other connected brands.
# Input:
# friends dictionary of (friend: count of number of followers with that friend) 
# followers list of all follower ids of the target brand
# Output:
# dictionary of (other_brand_id: correlation between that brand and target brand) 
def calculate_correlations(friends, followers, target_id):
    correlations = {}
    for friend in friends:
        current_ratio = 1.0 * friends[friend] / len(followers)
        if 1.0 * current_ratio >= 0.25 and current_ratio < 1.0:
            print 'calculate_correlations friend_id: ' + str(friend)
            other_followers = get_followers(friend)
            a = set(followers)
            b = set(other_followers)
            ratio = 2.0 * len(a - (a - b)) / (len(a) + len(b))
            correlations[friend] = ratio
        else:
            print 'ratio too low, skipping calculation: ' + str(friend)
    return correlations

# import socks
# import socket
# proxy = '96.240.24.35'
# port = 34089
# type = socks.PROXY_TYPE_SOCKS5
# socks.setdefaultproxy(type, proxy, port)
# socket.socket = socks.socksocket

# import httplib
# connect = httplib.HTTPConnection(proxy, timeout=20)

response = urllib2.urlopen('http://api.twitter.com/1/account/rate_limit_status.json')
html = json.loads(response.read())
print str(html['remaining_hits']) + ' api calls left.'

screen_name = 'coke'
id = get_id(screen_name)
print "Getting all followers of " + screen_name + "..."
follower_ids = get_followers(id)
print "Getting all friends of all followers..."
followers = create_followers_dict(follower_ids)
friends = {}
print "Creating dictionary of count of friends..."
update_friends_dict(friends, followers)
print "Writing to file..."
write_results_to_file('results', friends, len(followers))
print "Calculating correlations..."
correlations = calculate_correlations(friends, follower_ids, id)
print "Writing to file..."
write_results_to_file('correlations', correlations, len(correlations))

print "Done."
