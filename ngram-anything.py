import csv, re

class ngram():
	ngram = ''
	contentIDs = []
	instances = 0
	def __init__(self,ngram,contentID):
		self.ngram = ngram
		self.contentIDs = [contentID]
		self.instances = 1
	def addInstance(self,contentID):
		self.instances = self.instances + 1
		if contentID not in self.contentIDs:
			self.contentIDs.append(contentID)
class ngrammer():
	stopwords = ["a","about","above","after","again","against","all","am","an","and","any","are","as","at","be","because","been","before","being","below","between", "both", "but", "by", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from", "further", "had", "has", "have", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "it", "it's", "its", "itself", "let's", "me", "more", "most", "my", "myself", "nor", "of", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "she'd", "she'll", "she's", "should", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "we", "we'd", "we'll", "we're", "we've", "were", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "would", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves" ]
	wordboundaries = [' ','.',',','!','?','(',')','[',']','{','}','-','_','@','#','$','%','^','&','*','|','\\',"/","<",">","\n","\r\n"]
	ngrams = {}
	'''
	Imports a local CSV and outputs ngrams
	CSV format is content ID in first column and content in second
	'''
	def getNgrams(self,content,maxSize = 5):
		'''
		Break content up with regex for spaces, punctuation, and symbols into individual word chunks
		Loop through all word chunks and create 2-grams, then 3-grams then maxSize grams
		ngrams can't start or end with a stop word
		'''
		
		regex = "+|\\".join(self.wordboundaries)
		splitWords = re.split(regex,content)
		
		ngrams = []
		for thisGram in splitWords:
			if thisGram != '':
				ngrams.append(thisGram.lower())
		wordCount = len(ngrams)	
		output = []	
		if(wordCount > 1):
			for strLen in range(1,maxSize):
				for start in range(wordCount - strLen + 1):
					if(ngrams[start] not in self.stopwords and ngrams[(start + strLen - 1)] not in self.stopwords):
						thisGram = " ".join(ngrams[start:(start + strLen)]).strip()
						if(thisGram != '' and thisGram not in self.stopwords):
							output.append(thisGram)
		return output
	def addNgram(self,newNgram,contentID):
		ngramIndex = -1
		for index,thisNgram in self.ngrams.items():
			if(thisNgram.ngram == newNgram):
				ngramIndex = index
				break
		if(ngramIndex == -1):
			self.ngrams[len(self.ngrams.items())] = ngram(newNgram,contentID)
		else:
			self.ngrams[ngramIndex].addInstance(contentID)
	def readFromCSV(self,path):
		csvData = {}
		with open(path,'r', encoding="utf-8") as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			for row in csv_reader:
				csvData[row[0]] = row[1]
		
		for rowID,thisContent in csvData.items():
			print("Processing",rowID)
			for thisNgram in self.getNgrams(thisContent):
				self.addNgram(thisNgram,rowID)
		
		self.exportNgrams(path)
				
	def exportNgrams(self,path):
		csvPath = path.replace(".csv"," - ngrams.csv")
		with open(csvPath, 'w', newline = '', encoding="utf-8") as csvfile:
			output = csv.writer(csvfile, delimiter=',', quotechar='"')
			header = ['id','ngram','frequency']
			output.writerow(header)
			
			for index,thisNgram in self.ngrams.items():
				for thisID in self.ngrams[index].contentIDs:
					output.writerow([thisID,self.ngrams[index].ngram,self.ngrams[index].instances])
					
n = ngrammer();
n.readFromCSV("raw-content.csv")
