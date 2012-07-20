import urllib2
import psycopg2
import json
import itertools

def write_results_to_file(results, filename):
    extension = '.txt'
    f = open(filename + extension, 'w')
    for key in results:
        f.write(key + ': ' + results[key] + '\n')
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
            print e.code
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
            print e.code
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
        print follower_id
        followers[follower_id] = get_friends(follower_id)
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

import httplib
proxy = '202.166.217.161:80'
connect = httplib.HTTPConnection(proxy, timeout=20)

response = urllib2.urlopen('http://api.twitter.com/1/account/rate_limit_status.json')
html = json.loads(response.read())
print html['remaining_hits']

screen_name = 'coke'
print "Getting all followers of " + screen_name + "..."
follower_ids = get_followers(screen_name)
print "Getting all friends of all followers..."
followers = create_followers_dict(follower_ids)
friends = {}
print "Creating dictionary of count of friends..."
update_friends_dict(friends, followers)
print "Writing to file..."
write_results_to_file(friends, 'results')
print "Done."
