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

# Returns the user_ids of all followers of a specific user
# Input:
# user string of the user you want to find the followers of
# Output:
# array containing the list of user_ids of all followers for that user
def get_followers(user):
    followers = []
    base_url = 'http://api.twitter.com/1/followers/ids.json?&screen_name=%s&cursor=%s'
    screen_name = user
    cursor = -1
    while (cursor != 0):
        try:
            response = urllib2.urlopen(base_url % (screen_name, cursor))
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


def calculate_correlations(friends, target_id, num_followers):
    correlations = {}
    target_num_followers = num_followers
    for friend in friends:
        if 1.0 * friends[friend] / target_num_followers >= 0.3:
            print 'calculate_correlations friend_id: ' + str(friend)
            follower_ids = get_followers(get_screen_name(friend))
            followers = create_followers_dict(follower_ids)
            other_num_followers = len(followers)
            count = 0
            for follower in followers:
                if target_id in followers:
                    count += 1
            ratio = 2.0 * (count + friends[friend]) / (target_num_followers + other_num_followers)
            correlations[friend] = ratio
        else:
            print 'ratio too low, skipping calculation: ' + str(friend)
    return correlations

import httplib
proxy = '190.255.58.244:8080'
connect = httplib.HTTPConnection(proxy, timeout=20)

response = urllib2.urlopen('http://api.twitter.com/1/account/rate_limit_status.json')
html = json.loads(response.read())
print str(html['remaining_hits']) + ' api calls left.'

screen_name = 'coke'
id = get_id(screen_name)
print "Getting all followers of " + screen_name + "..."
follower_ids = get_followers(screen_name)
print "Getting all friends of all followers..."
followers = create_followers_dict(follower_ids)
friends = {}
print "Creating dictionary of count of friends..."
update_friends_dict(friends, followers)
print "Writing to file..."
write_results_to_file('results', friends, len(followers))
print "Calculating correlations..."
correlations = calculate_correlations(friends, id, len(followers))
write_results_to_file('correlations', correlations, len(correlations))

print "Done."
