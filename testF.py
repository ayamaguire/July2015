# Aya Maguire
# July 2015
# This test can be run on the log.txt file and the loclog.txt file that are
# created when the client/server main program is run. It makes sure that
# everything happened more or less as it should have.

import os

def fileinfo(path):
    filesize = os.stat(path)
    return filesize.st_size

logsize = fileinfo('log.txt')
loclogsize = fileinfo('loclog0.txt')
loclog = open('loclog0.txt')
dur = loclog.readline()
msize = loclog.readline()

if __name__ == "__main__":
    if logsize == 0:
        print "Nothing was written to the log. There was either no data sent, or the files were not properly closed."

    if loclogsize > msize:
        print "It looks like the local log files are not rolling over at the right time."

    if logsize != 0 and loclogsize <= msize:
        print "All tests OK."
