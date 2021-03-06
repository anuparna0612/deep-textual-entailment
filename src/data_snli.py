from w2vec import W2Vec
import numpy as np
from nltk.tokenize import word_tokenize
import string
from sklearn.preprocessing import LabelBinarizer

class SNLI:
	def __init__(self, w2vec):
		self.data = {}
		self.data['X'] = {}
		self.data['y'] = {}
		self.data['X']['train'],self.data['y']['train'] = self.loadData('train')
		self.data['X']['test'],self.data['y']['test'] = self.loadData('test')
		self.data['X']['dev'],self.data['y']['dev'] = self.loadData('dev')
		self.le = LabelBinarizer()
		self.w2vec = w2vec
		self.le.fit(['entailment','neutral','contradiction'])


	def loadData(self,dataset, onlyGoldLabels=True, tokenize=True):
		"""
		onlyGoldLabels = True
		some sentences don't have final label, only have the 5 labels from annotators which don't agree. Ignores such sentences

		tokenize:
		splits sentences into tokens
		"""
		y = []
		X = []
		with open('../data/snli/snli_1.0_'+dataset+'.txt') as datafile:
			prev = None
			for line in datafile:
				if prev is None:
					prev = line
					continue
				parts = line.split("\t")
				
				if onlyGoldLabels:
					if parts[0] == '-':
						continue
				else:
					raise NotImplementedError
				y.append(parts[0])
				X.append([self.preprocess(parts[5]),self.preprocess(parts[6])])
		return X, y

	def preprocess(self, sentence, removePunct = True, lowerCase = False):
		sentence = sentence.translate(None, string.punctuation)
		sentence = sentence.lower()
		return word_tokenize(sentence)
	
	def getMaxLengths(self):
		maxLen = [None,None]
		for ds in self.data['X']:
			for sent in self.data['X'][ds]:
				if maxLen[0] is None or len(sent[0])>maxLen[0]:
					maxLen[0] = len(sent[0])
				if maxLen[1] is None or len(sent[1])>maxLen[1]:
					maxLen[1] = len(sent[1])
		return maxLen

	def getX(self, dataset, start_index, end_index):
		premise = []
		hypothesis = []
		
		sentences = self.data['X'][dataset][start_index:end_index]
		
		for pair in sentences:
			prem = []
			for w in pair[0]:
				try:
					toappend = self.w2vec.convertWord(w)
				except KeyError:
					toappend = self.w2vec.unkWordRep()
				prem.append(toappend)
			premise.append(np.asarray(prem))
		
			hyp = []
			for w in pair[1]:
				try:
					toappend = self.w2vec.convertWord(w)
				except KeyError:
					toappend = self.w2vec.unkWordRep()
				hyp.append(toappend)
			hypothesis.append(np.asarray(hyp))

		rval = np.asarray(premise), np.asarray(hypothesis)
		return rval

	def getY(self, dataset, start_index=None, end_index=None):
		#converts label to 0,1,2
		if start_index is not None and end_index is not None:
			return self.le.transform(self.data['y'][dataset][start_index:end_index])
		else:
			return self.le.transform(self.data['y'][dataset])

	def getData(self, dataset):
		return self.getX(dataset), self.getY(dataset)

