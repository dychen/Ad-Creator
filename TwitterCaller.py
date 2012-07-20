## local modules
from ProxyList import *
from Exceptions import APIParseException
from Exceptions import APICursorException

## python modules
from datetime import *
import eventlet
from eventlet.green.httplib import *
from time import sleep
from copy import copy
from math import *
import socket


####
##  TwitterCaller
##  @author bslawski
##    Twitter API to TwitterCrawler thread interface
##    Holds a proxy address and port number, tracking
##    number of API calls made, switching proxies
##    automatically when a max number of calls have
##    been made.  Parses .json files and returns follower,
##    screenname, and tweet information
##
##  fields:
##    proxyList - ProxyList object to return new proxies
##
####

class TwitterCaller:

    ## constructor method
    def __init__(self, proxyList):
        ## ProxyList object to retrieve new proxy addresses from
        self.proxyList = ProxyList(proxyList, 100)

        ## number of attempted content lookups
        self.lookupAttempts = 0

        self.maxpage = 9999

        ## dictionary of month name to month number conversions
        self.months = {}
        self.months['Jan'] = 1
        self.months['Feb'] = 2
        self.months['Mar'] = 3
        self.months['Apr'] = 4
        self.months['May'] = 5
        self.months['Jun'] = 6
        self.months['Jul'] = 7
        self.months['Aug'] = 8
        self.months['Sep'] = 9
        self.months['Oct'] = 10
        self.months['Nov'] = 11
        self.months['Dec'] = 12


    ## Splits into multiple threads, each getting the 
    ## screename associated with an id in the given list.
    ## Returns the names found, as well as ids that could
    ## not be looked up
    def getNameMulti(self, pageids):
        foundNames = {}
        badIds = []
        nids = len(pageids)
        pool = eventlet.GreenPool()
        ngotten = 0
        returned = False
        for nametag in pool.imap(self.getNameMultiHelper, pageids):
            if returned:
                eventlet.kill()
            ngotten += 1
            name, tag = nametag
            if tag:
                id, username, popularity, importance, birthtime = name
                foundNames[id] = (username, popularity, importance, birthtime)
            else:
                badIds.append(name)
            if ngotten > nids * .8:
                returned = True
                return foundNames, badIds

        return foundNames, badIds


    ## Tries to look up a users screename given their id, 
    ## returning the name and True if successful, 
    ## and the original id and False if not
    def getNameMultiHelper(self, pageid):
##        self.getName(pageid)
        try:
            iddata = self.getName(pageid)
            return (iddata, True)
        except:
            return (pageid, False)


    ## Given a twitter page id as a string, retrieves and parses the
    ## user lookup .json file, returning as a string the user screen
    ## name corresponding to the id
    def getName(self, pageid):
        lookup = 'http://api.twitter.com/1/users/lookup.json?user_id=' \
                 + pageid
        content = self.getContent(lookup)

        try:
            name = ((content.split('\"screen_name\":\"'))[1]\
                   .split('\"'))[0]
            nfollowing = ((content.split('\"friends_count\":'))[1]\
                         .split(','))[0]
            nfollowing = int(nfollowing)
            nfollowers = ((content.split('\"followers_count\":'))[1]\
                         .split(','))[0]
            nfollowers = int(nfollowers)

            birthtime = (((content.split('\"created_at\":\"'))[1])\
                        .split('\",\"'))[0]

            birthtime = birthtime.split()
            birthtime = birthtime[5] + ':' + str(self.months[birthtime[1]]) + ':' + birthtime[2]

        ## Can't find the user data in the file
        except:
            raise APIParseException("Name Parse Error!")

        return pageid, name, nfollowers, log(float(nfollowing) / float(nfollowers), 10.), birthtime
    

    ## Splits into multiple threads to get the followers associated
    ## with each id in the given list.
    ## Found followers are returned as a list of lists, and ids 
    ## that could not be looked up are returned in a list
    def getFollowersMulti(self, pageids, maxpage=9999):
        self.maxpage = maxpage
        foundFollowers = []
        badIds = []
        pool = eventlet.GreenPool()
        hasReturned = False
        ngotten = 0
        nids = len(pageids)
        for idtag in pool.imap(self.getFollowersMultiHelper, pageids):
            if hasReturned:
                eventlet.kill()
            ids, tag = idtag
            if tag:
                foundFollowers.append(ids)
                ngotten += 1
            else:
                badIds.append(ids)
            if ngotten > nids * .5:
                hasReturned = True
                return foundFollowers, badIds

        return foundFollowers, badIds


    ## Tries to look up the followers associated with a given page,
    ## returning the list of followers and True if successful,
    ## and the original id and False if not
    def getFollowersMultiHelper(self, pageid):
        try:
            ids = self.getFollowers(pageid)
            return (ids, True)
        except:
            return (pageid, False)


    ## Given a twitter page id as a string, retrieves and parses the
    ## follwer .json file, returning as a list of strings the ids of
    ## the page
    def getFollowers(self, pageid, verbose=False):
        ## looks up the first page
        try:
            nextcur, newids = self.getCursorFollowers(pageid, '-1')
        except APICursorException:
            return self.getFollowers(pageid)
        page = 0

        ids = newids

        if self.maxpage == 0:
            return ids

        if verbose:
            print len(ids), 'followers'

        ## looks up subsequent pages if necessary
        while not nextcur == '0':
            page += 1
##            print 'page ', page, nextcur
            
            gotPage = False
            while not gotPage:
                try:
                    oldcur = nextcur
                    oldids = newids
                    nextcur, newids = self.getCursorFollowers(pageid, nextcur)
                    gotPage = True
                ## didn't work, try again
                except APICursorException:
                    nextcur = oldcur
                    newids = oldids
                    gotPage = False
                    
            ids.extend(newids)
            if verbose:
                print len(ids), 'followers'            

        return ids


    ## Helper function for getFollowers
    ## Retrieves a single page of a users followers
    def getCursorFollowers(self, pageid, cursor):
        lookup = 'http://api.twitter.com/1/followers/ids.json?cursor=' + \
                 cursor + '&user_id=' + pageid
        content = self.getContent(lookup)

        try:
            ids = (((content.split('\"ids\":['))[1]).split(']'))[0]
            ids = ids.split(',')
        ## Can't find followers to parse
        except:
            raise APICursorException("No followers!")

        try:
            nextcur = (((content.split('\"next_cursor_str\":\"'))[1])\
                       .split('\"'))[0]
        ## Can't find the cursor for the next page
        except:
            raise APICursorException("cursor error")

        return nextcur, ids
        

    ## Splits into multiple threads to look up the tweets
    ## from each user in the given list.
    ## Returns found tweets as a list of lists, as well as 
    ## a list of ids that could not be looked up
    def getTweetsMulti(self, userids):
        foundTweets = {}
        badIds = []
        nids = len(userids)
        pool = eventlet.GreenPool()
        ngotten = 0
        notFound = copy(userids)
        returned = False
        for tweettag in pool.imap(self.getTweetsMultiHelper, userids):
            if returned:
                eventlet.kill()
            ngotten += 1
            tweets, tag, id = tweettag
            if tag:
                foundTweets[id] = tweets
            else:
                badIds.append(id)

            notFound.remove(id)

            if ngotten > nids * .8:
                returned = True
                return foundTweets, badIds, notFound 

        return foundTweets, badIds, notFound


    ## Tries to get the tweets for a given user,
    ## returning the tweets and True if successful, 
    ## and the original screename and False if not,
    ## as well as the name
    def getTweetsMultiHelper(self, id):
        try:
            tweets = self.getTweets(id)
            return (tweets, True, id)
        except APIParseException:
            return (id, False, id)


    ## Given a twitter username as a string, retrieves and parses a
    ## .json file of the user's past week of tweets, returning the
    ## tweets as a list of tuples, with the julian time of the 
    ## tweet as the first element and the tweet string as the second
    def getTweets(self, userid):
        tweets = []

        lookup = 'http://api.twitter.com/1/statuses/user_timeline.json?count=200&user_id=' + userid
##        lookup = 'http://search.twitter.com/search.json?q=from:' + username
        content = self.getContent(lookup)

        try:
            tweetArr = content.split('},{')
            tweetArr[-1] = (tweetArr[-1].split('}]'))[0]

            for entry in tweetArr:
                tweet = ((entry.split('\"text\":\"')[1]).split('\",\"'))[0]
                tweettime = (((entry.split('\"created_at\":\"'))[1])\
                            .split('\",\"'))[0]
                tweettime = tweettime.split()[1:]
                tweet_t = tweettime[2].split(':')
                tweettime = datetime(int(tweettime[4]), \
                                self.months[tweettime[0]], \
                                int(tweettime[1]), \
                                int(tweet_t[0]), \
                                int(tweet_t[1]), \
                                int(tweet_t[2]))
                tweets.append((tweettime,tweet))
        except:
            raise APIParseException("No Tweets!")

        return tweets


    ## Retrieves a given url using the TwitterCaller's proxy,
    ## returning the read page as a string
    def getContent(self, lookup):
        self.lookupAttempts += 1
        try:
            proxy = self.proxyList.getProxy()
        except:
            sleep(1)
            return self.getContent(lookup)

##        connect = HTTPConnection(proxy, timeout=20)
##        connect.request("GET", lookup)
##        content = connect.getresponse().read()

        try:
            connect = HTTPConnection(proxy, timeout=6)
            connect.request("GET", lookup)
            content = connect.getresponse().read()

        ## lookup failed, lets get a new proxy
        except socket.timeout:
            if self.lookupAttempts > 20:
                return ''
##            print 'timeout'
            self.proxyList.reportBadProxy(proxy)
            content = self.getContent(lookup)

        except Exception,e:
##            print e
            self.proxyList.reportBadProxy(proxy)
            return ''

        self.lookupAttempts = 0
        return content


