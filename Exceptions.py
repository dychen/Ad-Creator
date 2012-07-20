####
##  ProxyGrabException
##  @author bslawski
##    Raised when an error occurs in looking up proxies from the proxy
##    list file.  Possible problems include an invalid proxy list file
##    name or an empty proxy list file.
##
####
class ProxyGrabException(Exception):

    def __init__(self, message):
        self.message = message
		
    def __str__(self):
        return repr(self.message)


####
##  APIParseException
##  @author bslawski
##    Raised when an error occurs in looking up or parsing twitter API
##    calls.  Possible problems include call limits, invalid page ids,
##    or lack of API data.
##
####
class APIParseException(Exception):

    def __init__(self, message):
        self.message = message
		
    def __str__(self):
        return repr(self.message)


####
##  APICursorException
##  @author bslawski
##    Raised when an error occurs in looking up or parsing a multi-paged
##    follower API call.  Possible problems inclue call limits and network
##    errors.
##
####
class APICursorException(Exception):

    def __init__(self, message):
        self.message = message
		
    def __str__(self):
        return repr(self.message)


####
##  SentimentTrainException
##  @author bslawski
##    Raised when an error occurs in training a Sentiment Analyzer.
##    Possible problems include missing or corrupted files.
##    
####
class SentimentTrainException(Exception):
    
    def __init__(self, message):
        self.message = message
		
    def __str__(self):
        return repr(self.message)


####
##  PlotException
##  @author bslawski
##
####
class PlotException(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)



