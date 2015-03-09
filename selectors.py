import pywsd

class WSDSelector:

	def __init__(self, method):
		if method == 'lesk':
			self.WSDfunction = self.getLeskSense
		elif method == 'leacho':
			self.WSDfunction = self.getLeaChoSense
		elif method == 'path':
			self.WSDfunction = self.getPathSense
		elif method == 'wupalmer':
			self.WSDfunction = self.getWuPalmerSense
		elif method == 'random':
			self.WSDfunction = self.getRandomSense
		elif method == 'first':
			self.WSDfunction = self.getFirstSense
		elif method == 'maxlemma':
			self.WSDfunction = self.getMaxLemmaSense
		else:
			self.WSDfunction = self.getLeskSense
		
	def selectCandidates(self, substitutions, victor_corpus):
		selected_substitutions = []				

		lexf = open(victor_corpus)
		for line in lexf:
			data = line.strip().split('\t')
			sent = data[0].strip()
			target = data[1].strip()
			head = int(data[2].strip())
		
			target_sense = self.WSDfunction.__call__(sent, target)
		
			candidates = []
			if target in substitutions.keys():
				candidates = substitutions[target]
		
			selected_candidates = set([])
			for candidate in candidates:
				candidate_sense = None
				try:
					unic = unicode(candidate)
					candidate_sense = self.WSDfunction.__call__(self.getCandidateSentence(sent, candidate, head), candidate)
				except UnicodeDecodeError:
					candidate_sense = None
				if target_sense or not candidate_sense:
					if not candidate_sense or candidate_sense==target_sense:
						selected_candidates.add(candidate)
			selected_substitutions.append(selected_candidates)
		lexf.close()

		return selected_substitutions

	def getLeskSense(self, sentence, target):
		try:
			result = pywsd.lesk.original_lesk(sentence, target)
			return result
		except IndexError:
			return None

	def getPathSense(self, sentence, target):
		try:
			result = pywsd.similarity.max_similarity(sentence, target, option="path", best=False)
			return result
		except IndexError:
			return None
	
	def getLeaChoSense(self, sentence, target):
		try:
			result = pywsd.similarity.max_similarity(sentence, target, option="lch", best=False)
			return result
		except IndexError:
			return None
			
	def getWuPalmerSense(self, sentence, target):
		try:
			result = pywsd.similarity.max_similarity(sentence, target, option="wup", best=False)
			return result
		except IndexError:
			return None
			
	def getRandomSense(self, sentence, target):
		try:
			result = pywsd.baseline.random_sense(target)
			return result
		except IndexError:
			return None
			
	def getFirstSense(self, sentence, target):
		try:
			result = pywsd.baseline.first_sense(target)
			return result
		except IndexError:
			return None
			
	def getMaxLemmaSense(self, sentence, target):
		try:
			result = pywsd.baseline.max_lemma_count(target)
			return result
		except IndexError:
			return None

	def getCandidateSentence(self, sentence, candidate, head):
		tokens = sentence.strip().split(' ')
		result = ''
		for i in range(0, head):
			result += tokens[i] + ' '
		result += candidate + ' '
		for i in range(head+1, len(tokens)):
			result += tokens[i] + ' '
		return result.strip()
