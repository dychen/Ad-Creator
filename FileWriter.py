import os

####
##  FileWriter
##  @author bslawski
##    Writes file content to several tmp files, writing to a
##    single file on close.  Allows for very large files to
##    be gradually written without holding the entire file in
##    memory.
##
##    init params:
##
##      filename - extensionless name of file to write to
##                 finished file will be 'filename.dat'
##
##      maxwrites - number of writes per tmp file
##                  a new tmp file is started when writes exceed this number
##
##      verbose - prints runtime output iff True
##
####

class FileWriter:
    
    ## constructor method    
    def __init__(self, filename, maxwrites, verbose):
        ## name of file to write to
        self.filename = filename
        ## max number of writes per tmp file
        self.maxwrites = maxwrites
        ## current number of writes to this tmp file
        self.writes = 0
        ## iff true, will print runtime info
        self.verbose = verbose
        ## index of tmp file being written
        self.tmpfileind = 0
        ## opens first tmp file for writing
        self.openTmpFile()


    ## writes given text string to tmp file
    ## incrementing write count and opening
    ## a new tmp file if necessary
    def write(self, text):
        self.writefile.write(text)
        self.writes += 1
        if self.writes >= self.maxwrites:
            self.writefile.close()
            self.tmpfileind += 1
            self.openTmpFile()
            self.writes = 0


    ## opens a tmp file with the current tmp file index 
    def openTmpFile(self):
        tmpfilename = self.filename + str(self.tmpfileind) + '.tmp'
        self.writefile = open(tmpfilename, 'w')


    ## writes tmp file contents to a single file
    ## removes tmp files
    def close(self):
        self.writefile.close()
        writefilename = self.filename + '.dat'
        if self.verbose:
            print 'writing ' + writefilename
        self.writefile = open(writefilename, 'w')
        for i in range(0, self.tmpfileind+1):
            if self.verbose:
                print '\t', i+1, ' / ', self.tmpfileind+1
            readfilename = self.filename + str(i) + '.tmp'
            readfile = open(readfilename, 'r')
            self.writefile.write(readfile.read())
            readfile.close()
            os.remove(readfilename)
        self.writefile.close()
        

def cleanUp(filename):
    if filename == 'all':
        cleanUp('positive')
        cleanUp('negative')
        cleanUp('target')
        cleanUp('tweets')
        return 

    outfile = open(filename + '.dat', 'w')
    i = 0
    while True:
        try:
            inname = filename + str(i) + '.tmp'
            infile = open(inname, 'r')
            outfile.write(infile.read())
            infile.close()
            os.remove(inname)
            i += 1
        except:
            outfile.close()
            break

   
## cleans up positive.dat, negative.dat, target.dat, tweets.dat
if __name__ == "__main__":
    cleanUp('all')
