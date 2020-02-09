#!/usr/bin/env python
# encoding: utf-8
import sys
import MySQLdb
import urllib2
import re
import Queue
from urlparse import urlparse
from time import time
from threading import Thread
from HTMLParser import HTMLParser

class database:
	def __init__(self):

		self.db = MySQLdb.connect('localhost','user_name','password','database_name')
	def getData(self,table):
		c = self.db.cursor()
		c.execute("SELECT * FROM `python_data`")

		data = c.fetchall()
		for row in data:
			print(row[1])

	def insertData(self,table,data):
		c = self.db.cursor()
		for thisData in data:
			sql = """INSERT INTO `python_data` (`data`) VALUES (%s)"""
			params = [thisData]
			c.execute(sql,params)
			self.db.commit()
   			print(c._last_executed)
class urlClass:
	def __init__(self, url = ''):
		self.url = url
		self.redirectURL = ''
		self.status = -1
		self.fetchStart = -1
		self.fetchEnd = -1
		self.content = ''


class linkExtractor(HTMLParser):
	
	def __init__(self):
		HTMLParser.__init__(self)
		self.links = []

	def handle_starttag(self,tag,attrs):
		if tag == 'a':
			for thisAttr in attrs:
				if 'href' in thisAttr:
					self.links.append(thisAttr[1])
class redirectHandler(urllib2.HTTPRedirectHandler):
    def http_response(self, request, response):
        return response
    def http_error_301(self, req, fp, code, msg, headers):
    	return None
    def http_error_302(self, req, fp, code, msg, headers):
    	return None

    https_response = http_response
class crawlWorker(Thread):
	def __init__(self,queue,crawlManager,name):
		Thread.__init__(self)
		self.queue = queue
		self.crawlManager = crawlManager
		self.name = name
	def run(self):
		while True:
			if self.crawlManager.status == 1:
				urlIndex = self.queue.get()
				try:
					self.crawlManager.urlData[urlIndex].startTime = time()
					self.crawlManager.attemptedRequest(urlIndex)
					print(self.name,'getting',self.crawlManager.urlData[urlIndex].url)

					parser = linkExtractor()
					try:
						response = urllib2.urlopen(self.crawlManager.urlData[urlIndex].url)
						response.encoding = 'utf-8'
						html = response.read(self.crawlManager.maxSize).decode('ascii','ignore')
						response.close()
						parser.feed(html)
						self.crawlManager.urlData[urlIndex].content = html
						self.crawlManager.urlData[urlIndex].status = 200
						self.crawlManager.urlData[urlIndex].endTime = time()
						for thisURL in parser.links:
							nextID = self.crawlManager.addURL(thisURL)
							if nextID > -1:
								self.queue.put(nextID)
					except urllib2.HTTPError, e:
						self.crawlManager.urlData[urlIndex].status = e.code
						if e.code == 301 or e.code == 302:
							self.crawlManager.urlData[urlIndex].redirectURL = e.headers['Location']
							nextID = self.crawlManager.addURL(e.headers['Location'])
							if nextID > -1:
								self.queue.put(nextID)
				except Exception as e:
					print('Error',e)
				finally:
					self.queue.task_done()
			else:
				self.queue.get()
				self.queue.task_done()


class crawlThreader:
	def __init__(self):
		self.workers = 5
		self.crawlManager = crawlManager()
		self.queue = Queue.Queue()

		opener = urllib2.build_opener(redirectHandler)
		urllib2.install_opener(opener)
	def startWorkers(self):
		for i in range(self.workers):
			worker = crawlWorker(self.queue,self.crawlManager,'worker' + str(i))
			worker.daemon = True
			worker.start()
	def crawlList(self,urls):
		for thisURL in urls:
			self.crawlManager.addURL(thisURL)
		for index,thisURL in self.crawlManager.urlData.iteritems():
			self.queue.put(index)
		self.crawlManager.status = 1
		self.startWorkers()
		self.queue.join()
		self.crawlManager.status = 2
	def crawlFromURL(self,url):
		self.crawlManager = crawlManager(url)
		self.queue.put(0)
		self.crawlManager.status = 1
		self.startWorkers()
		self.queue.join()
		self.crawlManager.status = 2

class crawlManager:
	def __init__(self, entryURL = ''):
		self.crawlStatus = -1
		self.requestedURLs = []
		self.maxURLs = 200
		self.maxSize = 10485760
		self.domain = ''
		self.matchDomain = True
		self.urlData = {}
		if entryURL != '':
			domainData = self.parseURL(entryURL)
			if domainData['host'] != '':
				self.domain = domainData['domain']
				self.addURL(self.urlFromComponents(domainData))
	def attemptedRequest(self,urlID):
		self.requestedURLs.append(urlID)
		if len(self.requestedURLs) >= self.maxURLs:
			self.status = -2
	def addURL(self,url = ''):
		status = -1
		if url != None or url != '':
			newURL = False
			urlPieces = self.parseURL(url)
			if urlPieces != None:
				if self.matchDomain == False:
					newURL = True
				elif urlPieces['domain'] == self.domain or urlPieces['domain'] == '':
					newURL = True
				if newURL:
					if urlPieces['domain'] == '':
						urlPieces['host'] = self.domain
					cleanURL = self.urlFromComponents(urlPieces)

					if cleanURL != None:
						inList = False
						for index,thisURL in list(self.urlData.iteritems()):
							if self.urlData[index].url == cleanURL:
								inList = True
								break
						if not inList:
							newIndex = len(self.urlData)
							self.urlData[newIndex] = urlClass(cleanURL)
							status = newIndex
		return status
	def parseURL(self,url = ''):
		if 'http://' not in url and 'https://' not in url:
			url = 'http://' + url
		parsedURL = urlparse(url)
		urlData = {}

		if parsedURL[1] != '' or parsedURL[2] != '':
			urlData['scheme'] = parsedURL[0]
			urlData['host'] = parsedURL[1]
			urlData['path'] = parsedURL[2]
			urlData['query'] = parsedURL[4]
			urlData['fragment'] = parsedURL[5]
			subdomain = re.match('(?:http[s]*\:\/\/)*(.*?)\.(?=[^\/]*\..{2,5})',url,re.I)
			if subdomain != None:
				urlData['subdomain'] = subdomain.group(1)
				urlData['domain'] = urlData['host'].replace(urlData['subdomain'],'').strip('.')
			else:
				urlData['domain'] = urlData['host']
			return urlData
		else:
			return None

	def urlFromComponents(self,parsedURL):
		if parsedURL['host'] != '':
			if parsedURL['scheme'] != '':
				url = parsedURL['scheme'] + '://' + parsedURL['host']
				if parsedURL['path'] != '':
					url = url + parsedURL['path']
				else:
					url = url + '/'
				if parsedURL['query'] != '':
					url = url + '?' + parsedURL['query']
				if parsedURL['fragment'] != '':
					url = url + '#' + parsedURL['fragment']
				return url
			else:
				return None
		else:
			return None

def main():
	print('Main thread started')

	try:
		startTime = time()
		print('Starting crawler')
		#print(sys.version)

		crawler = crawlThreader()
		url = 'example.com'
		crawler.crawlFromURL(url)

		for index,thisURL in crawler.crawlManager.urlData.items():
			print(crawler.crawlManager.urlData[index].status,crawler.crawlManager.urlData[index].url,len(crawler.crawlManager.urlData[index].content))

		print('Run Time',time() - startTime)

	except Exception, e:
		print(e)
	print(sys.argv[1:])

	
if __name__ == '__main__':
	main()
