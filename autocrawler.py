#!/usr/bin/python

#Import BeautifulSoup which I preffer over mechanize
from bs4 import BeautifulSoup
import datetime
import urllib2
import re
import subprocess
import time
import threading
import logging
import sys
##GLOBALS##
loadbalancerFile = open('loadbalancerIP.cfg','r')
loadbalancerIP = loadbalancerFile.read().strip()
loadbalancerFile.close()
print loadbalancerIP
currentAmountOfThreads = 0
fileAmount = 0
maxThreads = 0
listPointer = 0

listOfTimeAverages = [0,0,0,0,0,0,0,0,0,0]
threads = []

##FUNCTIONS##

def runbash(command):
    bashcommand = subprocess.call(command, shell=True)

def getbash(command):
    bashcommand = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    (bashOutput, err) = bashcommand.communicate()
    return bashOutput

#Function crawl
def crawl(weblink, depth):
    #If crawldepth lower than 2
    if depth < 2:
#        try:
        depth += 1
        #Open page
        html_page = urllib2.urlopen(weblink)
        #Create soup object
        soup = BeautifulSoup(html_page, 'html.parser')
        #For each link in page
        for link in soup.findAll('a'):
	      strippedLink = re.search('\[(.*?)\]', str(link)).group(1)
        for link in soup.findAll('img'):
              strippedLink = re.search('\[(.*?)\]', str(link)).group(1)
	      dummy =  getbash('wget -O /dev/null -o /dev/null ' + strippedLink)
	#imageQuality = getbash('curl ' + strippedLink)
	#print str(imageQuality) 

##CLASS##
class worker:
    number = 0
    lastTime = -1
    
    def __init__(self,numb):
        self.number = numb
        w = threading.Thread(target=self.work)
        w.start()
    def work(self):
       #while True:
        while(self.number <= maxThreads):
            start = time.time()
	    crawl('http://' + loadbalancerIP + '/index.php/?weight=2&ip=' + loadbalancerIP + ':8080',0)
            #logging.debug('Crawling ' + str(self.number))
            end = time.time()
            self.lastTime = end - start
        del threads[-1]

while True:
    print 'Innititating runtime with ' + str(fileAmount) + ' connections\n'   
    if (maxThreads < fileAmount):
        holder = maxThreads
        maxThreads = fileAmount

        for i in range(holder, fileAmount):
            #print i
            threads.append(worker(i+1))
        
    elif (maxThreads > fileAmount):
        maxThreads = fileAmount
    else:
        while (maxThreads == fileAmount):
            total = 0
	    lastFiveAvgs = 0
	    lastTenAvgs = 0
            #print fileAmount
            with open('numberOfThreads.cfg', 'r') as f:
                time.sleep(3)
                fileAmount = int(f.read())
		if fileAmount < 0:
		    sys.exit(0)
                #print threads
                for workingman in threads:
                    lastTime = workingman.lastTime
                    if lastTime != -1:
                        total += lastTime
                if maxThreads != 0:
                    total /= len(threads)
		    listOfTimeAverages[listPointer] = total
		    for i in range(listPointer - 4, listPointer + 1):
		        if listPointer < 0:
				listPointer += 10
			lastFiveAvgs += listOfTimeAverages[i]
		    lastFiveAvgs /= 5
		    for i in listOfTimeAverages:
			lastTenAvgs += i
		    lastTenAvgs /= 10
		    #print str(total) + ',' + str(lastFiveAvgs) + ',' + str(lastTenAvgs)
		    timefile = open('avgtime.log', 'a')
		    timefile.write(str(datetime.datetime.utcnow()) + ',' +  str(round(total, 2)) +
				  ',' + str(round(lastFiveAvgs, 2)) + ',' + str(round(lastTenAvgs, 2)) + '\n')
    		    timefile.close()
		    statsfile = open('currentstats.log', 'w')
		    statsfile.write(str(round(total,2)) + ',' + str(round(lastFiveAvgs,2)) + ',' 
				   + str(round(lastTenAvgs,2)) + '\n')
		    statsfile.close()
		    if listPointer == 9:
			listPointer = 0
		    else:
			listPointer += 1
                #logging.debug('The average is:' + str(total))
		else:
		    loadbalancerFile = open('loadbalancerIP.cfg','r')
		    loadbalancerIP = loadbalancerFile.read().strip()
		    loadbalancerFile.close()



#resultFile = open('result.txt', 'w')
#configFile = open('crawler.conf', 'r+')
#f.write(str(executionTime) + ' ' + sys.argv[2] + '\n')
