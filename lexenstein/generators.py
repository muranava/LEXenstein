import xml.etree.ElementTree as ET
import re
import urllib2 as urllib
from nltk.corpus import wordnet as wn
import subprocess
import nltk
import kenlm
import codecs

#Class for the Wordnet Generator
class WordnetFixedGenerator:

	def __init__(self, mat, nc):
		"""
		Creates a WordnetFixedGenerator instance.
	
		@param mat: MorphAdornerToolkit object.
		@param nc: NorvigCorrector object.
		"""
		self.mat = mat
		self.nc = nc

	def getSubstitutions(self, victor_corpus):
		"""
		Generates substitutions for the target words of a corpus in VICTOR format.
	
		@param victor_corpus: Path to a corpus in the VICTOR format.
		For more information about the file's format, refer to the LEXenstein Manual.
		@return: A dictionary that assigns target complex words to sets of candidate substitutions.
		Example: substitutions['perched'] = {'sat', 'roosted'}
		"""
		
		#Get initial set of substitutions:
		print('Getting initial set of substitutions...')
		substitutions_initial = self.getInitialSet(victor_corpus)
		
		#Get expanded set of substitutions:
		print('Getting expanded set of substitutions...')
		substitutions_expanded = self.getExpandedSet(substitutions_initial)

		#Get final substitutions:
		print('Inflecting substitutions...')
		substitutions_inflected = self.getInflectedSet(substitutions_expanded)

		#Return final set:
		print('Finished!')
		return substitutions_inflected

	def getInflectedSet(self, subs):
		#Create list of targets:
		targets = []
		
		#Create lists for inflection:
		toNothing = []
		toSingular = []
		toPlural = []
		toPAPEPA = []
		toPA = []
		toPRPA = []
		toPAPA = []
		toPR = []
		toComparative = []
		toSuperlative = []
		toOriginal = []
		
		#Fill lists:
		for target in subs.keys():
			targets.append(target)
			for pos in subs[target].keys():
				#Get cands for a target and tag combination:
				cands = list(subs[target][pos])
				
				#Add candidates to lists:
				if pos == 'NN':
					toSingular.extend(cands)
				elif pos == 'NNS':
					toPlural.extend(cands)
				elif pos == 'VB':
					toPAPEPA.extend(cands)
				elif pos == 'VBD':
					toPA.extend(cands)
				elif pos == 'VBG':
					toPRPA.extend(cands)
				elif pos == 'VBN':
					toPAPA.extend(cands)
				elif pos == 'VBP' or pos == 'VBZ':
					toPR.extend(cands)
				elif pos == 'JJR' or pos == 'RBR':
					toComparative.extend(cands)
				elif pos == 'JJS' or pos == 'RBS':
					toSuperlative.extend(cands)
				else:
					toNothing.extend(cands)
		#Lemmatize targets:
		targetsL = self.mat.lemmatizeWords(targets)
		
		#Lemmatize words:
		toNothingL = self.correctWords(self.mat.lemmatizeWords(toNothing))
		toSingularL = self.correctWords(self.mat.lemmatizeWords(toSingular))
		toPluralL = self.correctWords(self.mat.lemmatizeWords(toPlural))
		toPAPEPAL = self.correctWords(self.mat.lemmatizeWords(toPAPEPA))
		toPAL = self.correctWords(self.mat.lemmatizeWords(toPA))
		toPRPAL = self.correctWords(self.mat.lemmatizeWords(toPRPA))
		toPAPAL = self.correctWords(self.mat.lemmatizeWords(toPAPA))
		toPRL = self.correctWords(self.mat.lemmatizeWords(toPR))
		toComparativeL = self.correctWords(self.mat.lemmatizeWords(toComparative))
		toSuperlativeL = self.correctWords(self.mat.lemmatizeWords(toSuperlative))
		
		#Inflect nouns:
		singulars = self.correctWords(self.mat.inflectNouns(toSingularL, 'singular'))
		plurals = self.correctWords(self.mat.inflectNouns(toPluralL, 'plural'))
		
		#Inflect verbs:
		papepas = self.correctWords(self.mat.conjugateVerbs(toPAPEPAL, 'PAST_PERFECT_PARTICIPLE'))
		pas = self.correctWords(self.mat.conjugateVerbs(toPAL, 'PAST'))
		prpas = self.correctWords(self.mat.conjugateVerbs(toPRPAL, 'PRESENT_PARTICIPLE'))
		papas = self.correctWords(self.mat.conjugateVerbs(toPAPAL, 'PAST_PARTICIPLE'))
		prs = self.correctWords(self.mat.conjugateVerbs(toPRL, 'PRESENT'))
		
		#Inflect adjectives and adverbs:
		comparatives = self.correctWords(self.mat.inflectAdjectives(toComparativeL, 'comparative'))
		superlatives = self.correctWords(self.mat.inflectAdjectives(toSuperlativeL, 'superlative'))
		
		#Create maps:
		stemM = {}
		singularM = {}
		pluralM = {}
		papepaM = {}
		paM = {}
		prpaM = {}
		papaM = {}
		prM = {}
		comparativeM = {}
		superlativeM = {}

		for i in range(0, len(toNothing)):
			stemM[toNothing[i]] = toNothingL[i]
		for i in range(0, len(targets)):
			stemM[targets[i]] = targetsL[i]
		for i in range(0, len(toSingular)):
			stemM[toSingular[i]] = toSingularL[i]
			singularM[toSingular[i]] = singulars[i]
		for i in range(0, len(toPlural)):
			stemM[toPlural[i]] = toPluralL[i]
			pluralM[toPlural[i]] = plurals[i]
		for i in range(0, len(toPAPEPA)):
			stemM[toPAPEPA[i]] = toPAPEPAL[i]
			papepaM[toPAPEPA[i]] = papepas[i]
		for i in range(0, len(toPA)):
			stemM[toPA[i]] = toPAL[i]
			paM[toPA[i]] = pas[i]
		for i in range(0, len(toPRPA)):
			stemM[toPRPA[i]] = toPRPAL[i]
			prpaM[toPRPA[i]] = prpas[i]
		for i in range(0, len(toPAPA)):
			stemM[toPAPA[i]] = toPAPAL[i]
			papaM[toPAPA[i]] = papas[i]
		for i in range(0, len(toPR)):
			stemM[toPR[i]] = toPRL[i]
			prM[toPR[i]] = prs[i]
		for i in range(0, len(toComparative)):
			stemM[toComparative[i]] = toComparativeL[i]
			comparativeM[toComparative[i]] = comparatives[i]
		for i in range(0, len(toSuperlative)):
			stemM[toSuperlative[i]] = toSuperlativeL[i]
			superlativeM[toSuperlative[i]] = superlatives[i]
			
		#Create final substitutions:
		final_substitutions = {}
		for target in subs.keys():
			#Get lemma of target:
			targetL = stemM[target]
			
			#Create instance in final_substitutions:
			final_substitutions[target] = {}
			
			#Iterate through pos tags of target:
			for pos in subs[target].keys():
				#Create final cands:
				final_cands = set([])
				
				#Get cands for a target and tag combination:
				cands = list(subs[target][pos])
				
				#Add candidates to lists:
				if pos == 'NN':
					for cand in cands:
						if targetL!=stemM[cand]:
							final_cands.add(singularM[cand])
				elif pos == 'NNS':
					for cand in cands:
						if targetL!=stemM[cand]:
							final_cands.add(pluralM[cand])
				elif pos == 'VB':
					for cand in cands:
						if targetL!=stemM[cand]:
							final_cands.add(papepaM[cand])
				elif pos == 'VBD':
					for cand in cands:
						if targetL!=stemM[cand]:
							final_cands.add(paM[cand])
				elif pos == 'VBG':
					for cand in cands:
						if targetL!=stemM[cand]:
							final_cands.add(prpaM[cand])
				elif pos == 'VBN':
					for cand in cands:
						if targetL!=stemM[cand]:
							final_cands.add(papaM[cand])
				elif pos == 'VBP' or pos == 'VBZ':
					for cand in cands:
						if targetL!=stemM[cand]:
							final_cands.add(prM[cand])
				elif pos == 'JJR' or pos == 'RBR':
					for cand in cands:
						if targetL!=stemM[cand]:
							final_cands.add(comparativeM[cand])
				elif pos == 'JJS' or pos == 'RBS':
					for cand in cands:
						if targetL!=stemM[cand]:
							final_cands.add(superlativeM[cand])
				else:
					for cand in cands:
						if targetL!=stemM[cand]:
							final_cands.add(cand)
					
				#Add final cands to final substitutions:
				final_substitutions[target][pos] = final_cands
		return final_substitutions

	def getExpandedSet(self, subs):
		#Create lists for inflection:
		nouns = set([])
		verbs = set([])
		adjectives = set([])
		
		#Fill lists:
		for target in subs.keys():
			for pos in subs[target].keys():
				#Get cands for a target and tag combination:
				cands = list(subs[target][pos])
				
				#Add candidates to lists:
				if pos == 'NN' or pos == 'NNS':
					nouns.add(target)
				elif pos.startswith('V'):
					verbs.add(target)
				elif pos.startswith('J') or pos.startswith('RB'):
					adjectives.add(target)
		
		#Transform sets in lists:
		nouns = list(nouns)
		verbs = list(verbs)
		adjectives = list(adjectives)
		
		#Lemmatize words:
		nounsL = self.correctWords(self.mat.lemmatizeWords(nouns))
		verbsL = self.correctWords(self.mat.lemmatizeWords(verbs))
		adjectivesL = self.correctWords(self.mat.lemmatizeWords(adjectives))
		
		#Create lemma maps:
		nounM = {}
		verbM = {}
		adjectiveM = {}
		for i in range(0, len(nouns)):
			nounM[nouns[i]] = nounsL[i]
		for i in range(0, len(verbs)):
			verbM[verbs[i]] = verbsL[i]
		for i in range(0, len(adjectives)):
			adjectiveM[adjectives[i]] = adjectivesL[i]
		
		#Inflect words:
		plurals = self.correctWords(self.mat.inflectNouns(nounsL, 'plural'))
		pas = self.correctWords(self.mat.conjugateVerbs(verbsL, 'PAST'))
		prpas = self.correctWords(self.mat.conjugateVerbs(verbsL, 'PRESENT_PARTICIPLE'))
		papas = self.correctWords(self.mat.conjugateVerbs(verbsL, 'PAST_PARTICIPLE'))
		prs = self.correctWords(self.mat.conjugateVerbs(verbsL, 'PRESENT'))
		comparatives = self.correctWords(self.mat.inflectAdjectives(adjectives, 'comparative'))
		superlatives = self.correctWords(self.mat.inflectAdjectives(adjectives, 'superlative'))
		
		#Create inflected maps:
		pluralM = {}
		paM = {}
		prpaM = {}
		papaM = {}
		prM = {}
		comparativeM = {}
		superlativeM = {}
		for i in range(0, len(nouns)):
			pluralM[nouns[i]] = plurals[i]
		for i in range(0, len(verbs)):
			paM[verbs[i]] = pas[i]
			prpaM[verbs[i]] = prpas[i]
			papaM[verbs[i]] = papas[i]
			prM[verbs[i]] = prs[i]
		for i in range(0, len(adjectives)):
			comparativeM[adjectives[i]] = comparatives[i]
			superlativeM[adjectives[i]] = superlatives[i]
		
		#Create extended substitutions:
		substitutions_extended = {}
		for target in subs.keys():
			for pos in subs[target].keys():
				#Get cands for a target and tag combination:
				cands = list(subs[target][pos])
				
				#Add candidates to lists:
				if pos == 'NN' or pos == 'NNS':
					singularT = nounM[target]
					pluralT = pluralM[target]
					if singularT not in substitutions_extended:
						substitutions_extended[singularT] = {}
					if pluralT not in substitutions_extended:
						substitutions_extended[pluralT] = {}
					substitutions_extended[singularT]['NN'] = cands
					substitutions_extended[pluralT]['NNS'] = cands
				elif pos.startswith('V'):
					papepaT = verbM[target]
					paT = paM[target]
					prpaT = prpaM[target]
					papaT = papaM[target]
					prT = prM[target]
					if papepaT not in substitutions_extended:
						substitutions_extended[papepaT] = {}
					if paT not in substitutions_extended:
						substitutions_extended[paT] = {}
					if prpaT not in substitutions_extended:
						substitutions_extended[prpaT] = {}
					if papaT not in substitutions_extended:
						substitutions_extended[papaT] = {}
					if prT not in substitutions_extended:
						substitutions_extended[prT] = {}
					substitutions_extended[papepaT]['VB'] = cands
					substitutions_extended[paT]['VBD'] = cands
					substitutions_extended[prpaT]['VBG'] = cands
					substitutions_extended[papaT]['VBN'] = cands
					substitutions_extended[prT]['VBP'] = cands
				elif pos.startswith('J') or pos.startswith('RB'):
					originalT = adjectiveM[target]
					comparativeT = comparativeM[target]
					superlativeT = superlativeM[target]
					if originalT not in substitutions_extended:
						substitutions_extended[originalT] = {}
					if comparativeT not in substitutions_extended:
						substitutions_extended[comparativeT] = {}
					if superlativeT not in substitutions_extended:
						substitutions_extended[superlativeT] = {}
					substitutions_extended[originalT]['JJ'] = cands
					substitutions_extended[comparativeT]['JJR'] = cands
					substitutions_extended[superlativeT]['JJS'] = cands
		return substitutions_extended
		
	def getInitialSet(self, victor_corpus):
		substitutions_initial = {}
		lex = open(victor_corpus)
		for line in lex:
			data = line.strip().split('\t')
			sent = data[0].strip().split(' ')
			target = data[1].strip()
			head = int(data[2].strip())
			pos_data = nltk.pos_tag(sent)
			target_pos = pos_data[head][1].strip()
			target_wnpos = self.getWordnetPOS(target_pos)
			
			syns = wn.synsets(target)

			cands = set([])
			for syn in syns:
				for lem in syn.lemmas():
					candidate = self.cleanLemma(lem.name())
					if len(candidate.split(' '))==1:
						cands.add(candidate)
			if len(cands)>0:
				if target in substitutions_initial:
					substitutions_initial[target][target_pos] = cands
				else:
					substitutions_initial[target] = {target_pos:cands}
		lex.close()
		return substitutions_initial
		
	def correctWords(self, words):
		result = []
		for word in words:
			result.append(self.nc.correct(word))
		return result
		
	def getInflections(self, verbstems):
		data1 = self.mat.conjugateVerbs(verbstems, 'PAST_PERFECT_PARTICIPLE')
		data2 = self.mat.conjugateVerbs(verbstems, 'PAST_PARTICIPLE')
		data3 = self.mat.conjugateVerbs(verbstems, 'PRESENT_PARTICIPLE')
		return data1, data2, data3

	def getSingulars(self, plurstems):
		data = self.mat.inflectNouns(plurstems, 'singular')
		return data
		
	def getPlurals(self, singstems):
		data = self.mat.inflectNouns(singstems, 'plural')
		return data

	def getStems(self, sings, plurs, verbs):
		data = self.mat.lemmatizeWords(sings+plurs+verbs)
		rsings = []
		rplurs = []
		rverbs = []
		c = -1
		for sing in sings:
			c += 1
			if len(data[c])>0:
				rsings.append(data[c])
			else:
				rsings.append(sing)
		for plur in plurs:
			c += 1
			if len(data[c])>0:
				rplurs.append(data[c])
			else:
				rplurs.append(plur)
		for verb in verbs:
			c += 1
			if len(data[c])>0:
				rverbs.append(data[c])
			else:
				rverbs.append(verb)
		return rsings, rplurs, rverbs

	def cleanLemma(self, lem):
		result = ''
		aux = lem.strip().split('_')
		for word in aux:
			result += word + ' '
		return result.strip()
		
	def getWordnetPOS(self, pos):
		if pos[0] == 'N' or pos[0] == 'V' or pos == 'RBR' or pos == 'RBS':
			return pos[0].lower()
		elif pos[0] == 'J':
			return 'a'
		else:
			return None

class KauchakGenerator:

	def __init__(self, mat, parallel_pos_file, alignments_file, stop_words):
		"""
		Creates a KauchakGenerator instance.
	
		@param mat: MorphAdornerToolkit object.
		@param parallel_pos_file: Path to the parsed parallel corpus from which to extract substitutions.
		For more information about the file's format, refer to the LEXenstein Manual.
		@param alignments_file: Path to the alignments for the parsed parallel corpus from which to extract substitutions.
		For more information about the file's format, refer to the LEXenstein Manual.
		@param stop_words: Path to the file containing stop words of the desired language.
		The file must contain one stop word per line.
		"""
		self.mat = mat
		self.parallel_pos_file = parallel_pos_file
		self.alignments_file = alignments_file
		self.stop_words = set([word.strip() for word in open(stop_words)])

	def getSubstitutions(self, victor_corpus):
		"""
		Generates substitutions for the target words of a corpus in VICTOR format.
	
		@param victor_corpus: Path to a corpus in the VICTOR format.
		For more information about the file's format, refer to the LEXenstein Manual.
		@return: A dictionary that assigns target complex words to sets of candidate substitutions.
		Example: substitutions['perched'] = {'sat', 'roosted'}
		"""
		#Get candidate->pos map:
		print('Getting POS map...')
		target_pos = self.getPOSMap(victor_corpus)

		#Get initial set of substitutions:
		print('Getting initial set of substitutions...')
		substitutions_initial = self.getInitialSet(victor_corpus, target_pos)

		#Get final substitutions:
		print('Inflecting substitutions...')
		substitutions_inflected = self.getInflectedSet(substitutions_initial)

		#Return final set:
		print('Finished!')
		return substitutions_inflected

	def getInitialSet(self, victor_corpus, pos_map):
		substitutions_initial = {}

		targets = set([line.strip().split('\t')[1].strip() for line in open(victor_corpus)])

		fparallel = open(self.parallel_pos_file)
		falignments = open(self.alignments_file)

		for line in fparallel:
			data = line.strip().split('\t')
			source = data[0].strip().split(' ')
			target = data[1].strip().split(' ')

			alignments = set(falignments.readline().strip().split(' '))

			for alignment in alignments:
				adata = alignment.strip().split('-')
				left = int(adata[0].strip())
				right = int(adata[1].strip())
				leftraw = source[left].strip()
				leftp = leftraw.split('|||')[1].strip().lower()
				leftw = leftraw.split('|||')[0].strip()
				rightraw = target[right].strip()
				rightp = rightraw.split('|||')[1].strip().lower()
				rightw = rightraw.split('|||')[0].strip()

				if len(leftw)>0 and len(rightw)>0 and leftp!='nnp' and rightp!='nnp' and rightp==leftp and leftw not in self.stop_words and rightw not in self.stop_words and leftw!=rightw:
						if leftw in substitutions_initial.keys():
							if leftp in substitutions_initial[leftw].keys():
								substitutions_initial[leftw][leftp].add(rightw)
							else:
								substitutions_initial[leftw][leftp] = set(rightw)
						else:
							substitutions_initial[leftw] = {leftp:set([rightw])}
		fparallel.close()
		falignments.close()
		return substitutions_initial

	def getPOSMap(self, path):
		result = {}
		lex = open(path)
		for line in lex:
			data = line.strip().split('\t')
			sent = data[0].strip().lower().split(' ')
			target = data[1].strip().lower()
			head = int(data[2].strip())

			posd = nltk.pos_tag(sent)
			postarget = posd[head][1].lower().strip()
			if target in result.keys():
				result[target].add(postarget)
			else:
				result[target] = set([postarget])
		lex.close()
		return result

	def getInflectedSet(self, result):
		final_substitutions = {}

		#Get inflections:
		allkeys = sorted(list(result.keys()))

		singulars = {}
		plurals = {}
		verbs = {}

		singularsk = {}
		pluralsk = {}
		verbsk = {}

		for i in range(0, len(allkeys)):
			key = allkeys[i]
			leftw = key

			for leftp in result[leftw].keys():
				if leftp.startswith('n'):
					if leftp=='nns':
						pluralsk[leftw] = set([])
						for subst in result[key][leftp]:
							plurals[subst] = set([])
					else:
						singularsk[leftw] = set([])
						for subst in result[key][leftp]:
							singulars[subst] = set([])
				elif leftp.startswith('v'):
					verbsk[leftw] = {}
					for subst in result[key][leftp]:
						verbs[subst] = {}

		#------------------------------------------------------------------------------------------------

		#Generate keys input:
		singkeys = sorted(list(singularsk.keys()))
		plurkeys = sorted(list(pluralsk.keys()))
		verbkeys = sorted(list(verbsk.keys()))

		#Get stems:
		singstems, plurstems, verbstems = self.getStems(singkeys, plurkeys, verbkeys)

		#Get plurals:
		singres = self.getPlurals(singstems)

		#Get singulars:
		plurres = self.getSingulars(plurstems)

		#Get verb inflections:
		verbres1, verbres2, verbres3 = self.getInflections(verbstems)

		#Add information to dictionaries:
		for i in range(0, len(singkeys)):
			k = singkeys[i]
			singre = singres[i]
			singularsk[k] = singre
		for i in range(0, len(plurkeys)):
			k = plurkeys[i]
			plurre = plurres[i]
			pluralsk[k] = plurre
		for i in range(0, len(verbkeys)):
			k = verbkeys[i]
			verbre1 = verbres1[i]
			verbre2 = verbres2[i]
			verbre3 = verbres3[i]
			verbsk[k] = {'PAST_PERFECT_PARTICIPLE': verbre1, 'PAST_PARTICIPLE': verbre2, 'PRESENT_PARTICIPLE': verbre3}

		#------------------------------------------------------------------------------------------------

		#Generate substs input:
		singkeys = sorted(list(singulars.keys()))
		plurkeys = sorted(list(plurals.keys()))
		verbkeys = sorted(list(verbs.keys()))

		#Get stems:
		singstems, plurstems, verbstems = self.getStems(singkeys, plurkeys, verbkeys)

		#Get plurals:
		singres = self.getPlurals(singstems)

		#Get singulars:
		plurres = self.getSingulars(plurstems)

		#Get verb inflections:
		verbres1, verbres2, verbres3 = self.getInflections(verbstems)

		#Add information to dictionaries:
		for i in range(0, len(singkeys)):
			k = singkeys[i]
			singre = singres[i]
			singulars[k] = singre
		for i in range(0, len(plurkeys)):
			k = plurkeys[i]
			plurre = plurres[i]
			plurals[k] = plurre
		for i in range(0, len(verbkeys)):
			k = verbkeys[i]
			verbre1 = verbres1[i]
			verbre2 = verbres2[i]
			verbre3 = verbres3[i]
			verbs[k] = {'PAST_PERFECT_PARTICIPLE': verbre1, 'PAST_PARTICIPLE': verbre2, 'PRESENT_PARTICIPLE': verbre3}

		#------------------------------------------------------------------------------------------------

		#Generate final substitution list:
		for i in range(0, len(allkeys)):
			key = allkeys[i]
			leftw = key
			for leftp in result[leftw].keys():			

				#Add final version to candidates:
				if leftw not in final_substitutions.keys():
					final_substitutions[leftw] = result[key][leftp]
				else:
					final_substitutions[leftw] = final_substitutions[leftw].union(result[key][leftp])
				#If left is a noun:
				if leftp.startswith('n'):
					#If it is a plural:
					if leftp=='nns':
						plurl = pluralsk[leftw]
						newcands = set([])
						for candidate in result[key][leftp]:
							candplurl = plurals[candidate]
							newcands.add(candplurl)
						if plurl not in final_substitutions.keys():
							final_substitutions[plurl] = newcands
						else:
							final_substitutions[plurl] = final_substitutions[plurl].union(newcands)
					#If it is singular:
					else:
						singl = singularsk[leftw]
						newcands = set([])
						for candidate in result[key][leftp]:
							candsingl = singulars[candidate]
							newcands.add(candsingl)
						if singl not in final_substitutions.keys():
							final_substitutions[singl] = newcands
						else:
							final_substitutions[singl] = final_substitutions[singl].union(newcands)
				#If left is a verb:
				elif leftp.startswith('v'):
					for verb_tense in ['PAST_PERFECT_PARTICIPLE', 'PAST_PARTICIPLE', 'PRESENT_PARTICIPLE']:
						tensedl = verbsk[leftw][verb_tense]
						newcands = set([])
						for candidate in result[key][leftp]:
							candtensedl = verbs[candidate][verb_tense]
							newcands.add(candtensedl)
						if tensedl not in final_substitutions.keys():
							final_substitutions[tensedl] = newcands
						else:
							final_substitutions[tensedl] = final_substitutions[tensedl].union(newcands)
		return final_substitutions
		
	def getInflections(self, verbstems):
		data1 = self.mat.conjugateVerbs(verbstems, 'PAST_PERFECT_PARTICIPLE')
		data2 = self.mat.conjugateVerbs(verbstems, 'PAST_PARTICIPLE')
		data3 = self.mat.conjugateVerbs(verbstems, 'PRESENT_PARTICIPLE')
		return data1, data2, data3

	def getSingulars(self, plurstems):
		data = self.mat.inflectNouns(plurstems, 'singular')
		return data
		
	def getPlurals(self, singstems):
		data = self.mat.inflectNouns(singstems, 'plural')
		return data

	def getStems(self, sings, plurs, verbs):
		data = self.mat.lemmatizeWords(sings+plurs+verbs)
		rsings = []
		rplurs = []
		rverbs = []
		c = -1
		for sing in sings:
			c += 1
			if len(data[c])>0:
				rsings.append(data[c])
			else:
				rsings.append(sing)
		for plur in plurs:
			c += 1
			if len(data[c])>0:
				rplurs.append(data[c])
			else:
				rplurs.append(plur)
		for verb in verbs:
			c += 1
			if len(data[c])>0:
				rverbs.append(data[c])
			else:
				rverbs.append(verb)
		return rsings, rplurs, rverbs

class YamamotoGenerator:

	def __init__(self, mat, dictionary_key):
		"""
		Creates a YamamotoGenerator instance.
	
		@param mat: MorphAdornerToolkit object.
		@param dictionary_key: Key for the Merriam Dictionary.
		For more information on how to get the key for free, please refer to the LEXenstein Manual
		"""
		self.mat = mat
		self.dictionary_key = dictionary_key

	def getSubstitutions(self, victor_corpus):
		"""
		Generates substitutions for the target words of a corpus in VICTOR format.
	
		@param victor_corpus: Path to a corpus in the VICTOR format.
		For more information about the file's format, refer to the LEXenstein Manual.
		@return: A dictionary that assigns target complex words to sets of candidate substitutions.
		Example: substitutions['perched'] = {'sat', 'roosted'}
		"""
		#Get initial set of substitutions:
		print('Getting initial set of substitutions...')
		substitutions_initial = self.getInitialSet(victor_corpus)

		#Get final substitutions:
		print('Inflecting substitutions...')
		substitutions_inflected = self.getInflectedSet(substitutions_initial)

		#Return final set:
		print('Finished!')
		return substitutions_inflected

	def getInflectedSet(self, result):
		final_substitutions = {}

		#Get inflections:
		allkeys = sorted(list(result.keys()))

		singulars = {}
		plurals = {}
		verbs = {}

		singularsk = {}
		pluralsk = {}
		verbsk = {}

		for i in range(0, len(allkeys)):
			key = allkeys[i]
			leftw = key

			for leftp in result[leftw].keys():
				if leftp.startswith('n'):
					if leftp=='nns':
						pluralsk[leftw] = set([])
						for subst in result[key][leftp]:
							plurals[subst] = set([])
					else:
						singularsk[leftw] = set([])
						for subst in result[key][leftp]:
							singulars[subst] = set([])
				elif leftp.startswith('v'):
					verbsk[leftw] = {}
					for subst in result[key][leftp]:
						verbs[subst] = {}

		#------------------------------------------------------------------------------------------------

		#Generate keys input:
		singkeys = sorted(list(singularsk.keys()))
		plurkeys = sorted(list(pluralsk.keys()))
		verbkeys = sorted(list(verbsk.keys()))

		#Get stems:
		singstems, plurstems, verbstems = self.getStems(singkeys, plurkeys, verbkeys)

		#Get plurals:
		singres = self.getPlurals(singstems)

		#Get singulars:
		plurres = self.getSingulars(plurstems)

		#Get verb inflections:
		verbres1, verbres2, verbres3 = self.getInflections(verbstems)

		#Add information to dictionaries:
		for i in range(0, len(singkeys)):
			k = singkeys[i]
			singre = singres[i]
			singularsk[k] = singre
		for i in range(0, len(plurkeys)):
			k = plurkeys[i]
			plurre = plurres[i]
			pluralsk[k] = plurre
		for i in range(0, len(verbkeys)):
			k = verbkeys[i]
			verbre1 = verbres1[i]
			verbre2 = verbres2[i]
			verbre3 = verbres3[i]
			verbsk[k] = {'PAST_PERFECT_PARTICIPLE': verbre1, 'PAST_PARTICIPLE': verbre2, 'PRESENT_PARTICIPLE': verbre3}

		#------------------------------------------------------------------------------------------------

		#Generate substs input:
		singkeys = sorted(list(singulars.keys()))
		plurkeys = sorted(list(plurals.keys()))
		verbkeys = sorted(list(verbs.keys()))

		#Get stems:
		singstems, plurstems, verbstems = self.getStems(singkeys, plurkeys, verbkeys)

		#Get plurals:
		singres = self.getPlurals(singstems)

		#Get singulars:
		plurres = self.getSingulars(plurstems)

		#Get verb inflections:
		verbres1, verbres2, verbres3 = self.getInflections(verbstems)

		#Add information to dictionaries:
		for i in range(0, len(singkeys)):
			k = singkeys[i]
			singre = singres[i]
			singulars[k] = singre
		for i in range(0, len(plurkeys)):
			k = plurkeys[i]
			plurre = plurres[i]
			plurals[k] = plurre
		for i in range(0, len(verbkeys)):
			k = verbkeys[i]
			verbre1 = verbres1[i]
			verbre2 = verbres2[i]
			verbre3 = verbres3[i]
			verbs[k] = {'PAST_PERFECT_PARTICIPLE': verbre1, 'PAST_PARTICIPLE': verbre2, 'PRESENT_PARTICIPLE': verbre3}

		#------------------------------------------------------------------------------------------------

		#Generate final substitution list:
		for i in range(0, len(allkeys)):
			key = allkeys[i]
			leftw = key
			for leftp in result[leftw].keys():			

				#Add final version to candidates:
				if leftw not in final_substitutions.keys():
					final_substitutions[leftw] = result[key][leftp]
				else:
					final_substitutions[leftw] = final_substitutions[leftw].union(result[key][leftp])
				#If left is a noun:
				if leftp.startswith('n'):
					#If it is a plural:
					if leftp=='nns':
						plurl = pluralsk[leftw]
						newcands = set([])
						for candidate in result[key][leftp]:
							candplurl = plurals[candidate]
							newcands.add(candplurl)
						if plurl not in final_substitutions.keys():
							final_substitutions[plurl] = newcands
						else:
							final_substitutions[plurl] = final_substitutions[plurl].union(newcands)
					#If it is singular:
					else:
						singl = singularsk[leftw]
						newcands = set([])
						for candidate in result[key][leftp]:
							candsingl = singulars[candidate]
							newcands.add(candsingl)
						if singl not in final_substitutions.keys():
							final_substitutions[singl] = newcands
						else:
							final_substitutions[singl] = final_substitutions[singl].union(newcands)
				#If left is a verb:
				elif leftp.startswith('v'):
					for verb_tense in ['PAST_PERFECT_PARTICIPLE', 'PAST_PARTICIPLE', 'PRESENT_PARTICIPLE']:
						tensedl = verbsk[leftw][verb_tense]
						newcands = set([])
						for candidate in result[key][leftp]:
							candtensedl = verbs[candidate][verb_tense]
							newcands.add(candtensedl)
						if tensedl not in final_substitutions.keys():
							final_substitutions[tensedl] = newcands
						else:
							final_substitutions[tensedl] = final_substitutions[tensedl].union(newcands)
		return final_substitutions
		
	def getInflections(self, verbstems):
		data1 = self.mat.conjugateVerbs(verbstems, 'PAST_PERFECT_PARTICIPLE')
		data2 = self.mat.conjugateVerbs(verbstems, 'PAST_PARTICIPLE')
		data3 = self.mat.conjugateVerbs(verbstems, 'PRESENT_PARTICIPLE')
		return data1, data2, data3

	def getSingulars(self, plurstems):
		data = self.mat.inflectNouns(plurstems, 'singular')
		return data
		
	def getPlurals(self, singstems):
		data = self.mat.inflectNouns(singstems, 'plural')
		return data

	def getStems(self, sings, plurs, verbs):
		data = self.mat.lemmatizeWords(sings+plurs+verbs)
		rsings = []
		rplurs = []
		rverbs = []
		c = -1
		for sing in sings:
			c += 1
			if len(data[c])>0:
				rsings.append(data[c])
			else:
				rsings.append(sing)
		for plur in plurs:
			c += 1
			if len(data[c])>0:
				rplurs.append(data[c])
			else:
				rplurs.append(plur)
		for verb in verbs:
			c += 1
			if len(data[c])>0:
				rverbs.append(data[c])
			else:
				rverbs.append(verb)
		return rsings, rplurs, rverbs

	def getInitialSet(self, victor_corpus):
		substitutions_initial = {}

		lex = open(victor_corpus)
		for line in lex:
			data = line.strip().split('\t')
			target = data[1].strip()
			head = int(data[2].strip())

			url = 'http://www.dictionaryapi.com/api/v1/references/collegiate/xml/' + target + '?key=' + self.dictionary_key
			conn = urllib.urlopen(url)
			root = ET.fromstring(conn.read())

			newline = target + '\t'
			cands = {}

			entries = root.iter('entry')
			for entry in entries:
				node_pos = entry.find('fl')
				if node_pos != None:
					node_pos = node_pos.text.strip()[0].lower()
					if node_pos not in cands.keys():
						cands[node_pos] = set([])
				for definition in entry.iter('dt'):
					if definition.text!=None:
						text = definition.text.strip()
						text = text[1:len(text)]
						tokens = nltk.word_tokenize(text)
						postags = nltk.pos_tag(tokens)
						for p in postags:
							postag = p[1].strip()[0].lower()
							cand = p[0].strip()
							if postag==node_pos:
								try:
									test = codecs.ascii_encode(cand)
									cands[node_pos].add(cand)
								except UnicodeEncodeError:
									cands = cands
			for pos in cands.keys():
				if target in cands[pos]:
					cands[pos].remove(target)
			if len(cands.keys())>0:
				substitutions_initial[target] = cands
		lex.close()
		return substitutions_initial

class MerriamGenerator:

	def __init__(self, mat, thesaurus_key):
		"""
		Creates a MerriamGenerator instance.
	
		@param mat: MorphAdornerToolkit object.
		@param thesaurus_key: Key for the Merriam Thesaurus.
		For more information on how to get the key for free, please refer to the LEXenstein Manual
		"""
		self.mat = mat
		self.thesaurus_key = thesaurus_key

	def getSubstitutions(self, victor_corpus):
		"""
		Generates substitutions for the target words of a corpus in VICTOR format.
	
		@param victor_corpus: Path to a corpus in the VICTOR format.
		For more information about the file's format, refer to the LEXenstein Manual.
		@return: A dictionary that assigns target complex words to sets of candidate substitutions.
		Example: substitutions['perched'] = {'sat', 'roosted'}
		"""
		#Get initial set of substitutions:
		print('Getting initial set of substitutions...')
		substitutions_initial = self.getInitialSet(victor_corpus)

		#Get final substitutions:
		print('Inflecting substitutions...')
		substitutions_inflected = self.getInflectedSet(substitutions_initial)

		#Return final set:
		print('Finished!')
		return substitutions_inflected

	def getInflectedSet(self, result):
		final_substitutions = {}

		#Get inflections:
		allkeys = sorted(list(result.keys()))

		singulars = {}
		plurals = {}
		verbs = {}

		singularsk = {}
		pluralsk = {}
		verbsk = {}

		for i in range(0, len(allkeys)):
			key = allkeys[i]
			leftw = key

			for leftp in result[leftw].keys():
				if leftp.startswith('n'):
					if leftp=='nns':
						pluralsk[leftw] = set([])
						for subst in result[key][leftp]:
							plurals[subst] = set([])
					else:
						singularsk[leftw] = set([])
						for subst in result[key][leftp]:
							singulars[subst] = set([])
				elif leftp.startswith('v'):
					verbsk[leftw] = {}
					for subst in result[key][leftp]:
						verbs[subst] = {}

		#------------------------------------------------------------------------------------------------

		#Generate keys input:
		singkeys = sorted(list(singularsk.keys()))
		plurkeys = sorted(list(pluralsk.keys()))
		verbkeys = sorted(list(verbsk.keys()))

		#Get stems:
		singstems, plurstems, verbstems = self.getStems(singkeys, plurkeys, verbkeys)

		#Get plurals:
		singres = self.getPlurals(singstems)

		#Get singulars:
		plurres = self.getSingulars(plurstems)

		#Get verb inflections:
		verbres1, verbres2, verbres3 = self.getInflections(verbstems)

		#Add information to dictionaries:
		for i in range(0, len(singkeys)):
			k = singkeys[i]
			singre = singres[i]
			singularsk[k] = singre
		for i in range(0, len(plurkeys)):
			k = plurkeys[i]
			plurre = plurres[i]
			pluralsk[k] = plurre
		for i in range(0, len(verbkeys)):
			k = verbkeys[i]
			verbre1 = verbres1[i]
			verbre2 = verbres2[i]
			verbre3 = verbres3[i]
			verbsk[k] = {'PAST_PERFECT_PARTICIPLE': verbre1, 'PAST_PARTICIPLE': verbre2, 'PRESENT_PARTICIPLE': verbre3}

		#------------------------------------------------------------------------------------------------

		#Generate substs input:
		singkeys = sorted(list(singulars.keys()))
		plurkeys = sorted(list(plurals.keys()))
		verbkeys = sorted(list(verbs.keys()))

		#Get stems:
		singstems, plurstems, verbstems = self.getStems(singkeys, plurkeys, verbkeys)

		#Get plurals:
		singres = self.getPlurals(singstems)

		#Get singulars:
		plurres = self.getSingulars(plurstems)

		#Get verb inflections:
		verbres1, verbres2, verbres3 = self.getInflections(verbstems)

		#Add information to dictionaries:
		for i in range(0, len(singkeys)):
			k = singkeys[i]
			singre = singres[i]
			singulars[k] = singre
		for i in range(0, len(plurkeys)):
			k = plurkeys[i]
			plurre = plurres[i]
			plurals[k] = plurre
		for i in range(0, len(verbkeys)):
			k = verbkeys[i]
			verbre1 = verbres1[i]
			verbre2 = verbres2[i]
			verbre3 = verbres3[i]
			verbs[k] = {'PAST_PERFECT_PARTICIPLE': verbre1, 'PAST_PARTICIPLE': verbre2, 'PRESENT_PARTICIPLE': verbre3}

		#------------------------------------------------------------------------------------------------

		#Generate final substitution list:
		for i in range(0, len(allkeys)):
			key = allkeys[i]
			leftw = key
			for leftp in result[leftw].keys():			

				#Add final version to candidates:
				if leftw not in final_substitutions.keys():
					final_substitutions[leftw] = result[key][leftp]
				else:
					final_substitutions[leftw] = final_substitutions[leftw].union(result[key][leftp])
				#If left is a noun:
				if leftp.startswith('n'):
					#If it is a plural:
					if leftp=='nns':
						plurl = pluralsk[leftw]
						newcands = set([])
						for candidate in result[key][leftp]:
							candplurl = plurals[candidate]
							newcands.add(candplurl)
						if plurl not in final_substitutions.keys():
							final_substitutions[plurl] = newcands
						else:
							final_substitutions[plurl] = final_substitutions[plurl].union(newcands)
					#If it is singular:
					else:
						singl = singularsk[leftw]
						newcands = set([])
						for candidate in result[key][leftp]:
							candsingl = singulars[candidate]
							newcands.add(candsingl)
						if singl not in final_substitutions.keys():
							final_substitutions[singl] = newcands
						else:
							final_substitutions[singl] = final_substitutions[singl].union(newcands)
				#If left is a verb:
				elif leftp.startswith('v'):
					for verb_tense in ['PAST_PERFECT_PARTICIPLE', 'PAST_PARTICIPLE', 'PRESENT_PARTICIPLE']:
						tensedl = verbsk[leftw][verb_tense]
						newcands = set([])
						for candidate in result[key][leftp]:
							candtensedl = verbs[candidate][verb_tense]
							newcands.add(candtensedl)
						if tensedl not in final_substitutions.keys():
							final_substitutions[tensedl] = newcands
						else:
							final_substitutions[tensedl] = final_substitutions[tensedl].union(newcands)
		return final_substitutions
		
	def getInflections(self, verbstems):
		data1 = self.mat.conjugateVerbs(verbstems, 'PAST_PERFECT_PARTICIPLE')
		data2 = self.mat.conjugateVerbs(verbstems, 'PAST_PARTICIPLE')
		data3 = self.mat.conjugateVerbs(verbstems, 'PRESENT_PARTICIPLE')
		return data1, data2, data3

	def getSingulars(self, plurstems):
		data = self.mat.inflectNouns(plurstems, 'singular')
		return data
		
	def getPlurals(self, singstems):
		data = self.mat.inflectNouns(singstems, 'plural')
		return data

	def getStems(self, sings, plurs, verbs):
		data = self.mat.lemmatizeWords(sings+plurs+verbs)
		rsings = []
		rplurs = []
		rverbs = []
		c = -1
		for sing in sings:
			c += 1
			if len(data[c])>0:
				rsings.append(data[c])
			else:
				rsings.append(sing)
		for plur in plurs:
			c += 1
			if len(data[c])>0:
				rplurs.append(data[c])
			else:
				rplurs.append(plur)
		for verb in verbs:
			c += 1
			if len(data[c])>0:
				rverbs.append(data[c])
			else:
				rverbs.append(verb)
		return rsings, rplurs, rverbs

	def getInitialSet(self, victor_corpus):
		substitutions_initial = {}

		lex = open(victor_corpus)
		for line in lex:
			data = line.strip().split('\t')
			target = data[1].strip()
			url = 'http://www.dictionaryapi.com/api/v1/references/thesaurus/xml/' + target + '?key=' + self.thesaurus_key
			conn = urllib.urlopen(url)
			root = ET.fromstring(conn.read())
			root = root.findall('entry')

			cands = {}
			if len(root)>0:
				for root_node in root:
					node_pos = root_node.find('fl')
					if node_pos != None:
						node_pos = node_pos.text.strip()[0].lower()
						if node_pos not in cands.keys():
							cands[node_pos] = set([])
					syn = None
					for sense in root_node.iter('sens'):
						syndata = sense.findall('syn')
						if len(syndata)>0:
							syn = syndata[0]
					if syn:
						res = ''
						for snip in syn.itertext():
							res += snip + ' '
						finds = re.findall('\([^\)]+\)', res)
						for find in finds:
							res = res.replace(find, '')

						synonyms = [s.strip() for s in res.split(',')]

						for synonym in synonyms:
							if len(synonym.split(' '))==1:
								try:
									test = codecs.ascii_encode(synonym)
									cands[node_pos].add(synonym)
								except UnicodeEncodeError:
									cands = cands
			for pos in cands.keys():
				if target in cands[pos]:
					cands[pos].remove(target)
			if len(cands.keys())>0:
				substitutions_initial[target] = cands
		lex.close()
		return substitutions_initial

#Class for the Wordnet Generator
class WordnetGenerator:

	def __init__(self, mat):
		"""
		Creates a WordnetGenerator instance.
	
		@param mat: MorphAdornerToolkit object.
		"""
		self.mat = mat

	def getSubstitutions(self, victor_corpus):
		"""
		Generates substitutions for the target words of a corpus in VICTOR format.
	
		@param victor_corpus: Path to a corpus in the VICTOR format.
		For more information about the file's format, refer to the LEXenstein Manual.
		@return: A dictionary that assigns target complex words to sets of candidate substitutions.
		Example: substitutions['perched'] = {'sat', 'roosted'}
		"""
		
		#Get initial set of substitutions:
		print('Getting initial set of substitutions...')
		substitutions_initial = self.getInitialSet(victor_corpus)

		#Get final substitutions:
		print('Inflecting substitutions...')
		substitutions_inflected = self.getInflectedSet(substitutions_initial)

		#Return final set:
		print('Finished!')
		return substitutions_inflected

	def getInflectedSet(self, result):
		final_substitutions = {}

		#Get inflections:
		allkeys = sorted(list(result.keys()))

		singulars = {}
		plurals = {}
		verbs = {}

		singularsk = {}
		pluralsk = {}
		verbsk = {}

		for i in range(0, len(allkeys)):
			key = allkeys[i]
			leftw = key

			for leftp in result[leftw].keys():
				if leftp.startswith('n'):
					if leftp=='nns':
						pluralsk[leftw] = set([])
						for subst in result[key][leftp]:
							plurals[subst] = set([])
					else:
						singularsk[leftw] = set([])
						for subst in result[key][leftp]:
							singulars[subst] = set([])
				elif leftp.startswith('v'):
					verbsk[leftw] = {}
					for subst in result[key][leftp]:
						verbs[subst] = {}

		#------------------------------------------------------------------------------------------------

		#Generate keys input:
		singkeys = sorted(list(singularsk.keys()))
		plurkeys = sorted(list(pluralsk.keys()))
		verbkeys = sorted(list(verbsk.keys()))

		#Get stems:
		singstems, plurstems, verbstems = self.getStems(singkeys, plurkeys, verbkeys)

		#Get plurals:
		singres = self.getPlurals(singstems)

		#Get singulars:
		plurres = self.getSingulars(plurstems)

		#Get verb inflections:
		verbres1, verbres2, verbres3 = self.getInflections(verbstems)

		#Add information to dictionaries:
		for i in range(0, len(singkeys)):
			k = singkeys[i]
			singre = singres[i]
			singularsk[k] = singre
		for i in range(0, len(plurkeys)):
			k = plurkeys[i]
			plurre = plurres[i]
			pluralsk[k] = plurre
		for i in range(0, len(verbkeys)):
			k = verbkeys[i]
			verbre1 = verbres1[i]
			verbre2 = verbres2[i]
			verbre3 = verbres3[i]
			verbsk[k] = {'PAST_PERFECT_PARTICIPLE': verbre1, 'PAST_PARTICIPLE': verbre2, 'PRESENT_PARTICIPLE': verbre3}

		#------------------------------------------------------------------------------------------------

		#Generate substs input:
		singkeys = sorted(list(singulars.keys()))
		plurkeys = sorted(list(plurals.keys()))
		verbkeys = sorted(list(verbs.keys()))

		#Get stems:
		singstems, plurstems, verbstems = self.getStems(singkeys, plurkeys, verbkeys)

		#Get plurals:
		singres = self.getPlurals(singstems)

		#Get singulars:
		plurres = self.getSingulars(plurstems)

		#Get verb inflections:
		verbres1, verbres2, verbres3 = self.getInflections(verbstems)

		#Add information to dictionaries:
		for i in range(0, len(singkeys)):
			k = singkeys[i]
			singre = singres[i]
			singulars[k] = singre
		for i in range(0, len(plurkeys)):
			k = plurkeys[i]
			plurre = plurres[i]
			plurals[k] = plurre
		for i in range(0, len(verbkeys)):
			k = verbkeys[i]
			verbre1 = verbres1[i]
			verbre2 = verbres2[i]
			verbre3 = verbres3[i]
			verbs[k] = {'PAST_PERFECT_PARTICIPLE': verbre1, 'PAST_PARTICIPLE': verbre2, 'PRESENT_PARTICIPLE': verbre3}

		#------------------------------------------------------------------------------------------------

		#Generate final substitution list:
		for i in range(0, len(allkeys)):
			key = allkeys[i]
			leftw = key
			for leftp in result[leftw].keys():			

				#Add final version to candidates:
				if leftw not in final_substitutions.keys():
					final_substitutions[leftw] = result[key][leftp]
				else:
					final_substitutions[leftw] = final_substitutions[leftw].union(result[key][leftp])
				#If left is a noun:
				if leftp.startswith('n'):
					#If it is a plural:
					if leftp=='nns':
						plurl = pluralsk[leftw]
						newcands = set([])
						for candidate in result[key][leftp]:
							candplurl = plurals[candidate]
							newcands.add(candplurl)
						if plurl not in final_substitutions.keys():
							final_substitutions[plurl] = newcands
						else:
							final_substitutions[plurl] = final_substitutions[plurl].union(newcands)
					#If it is singular:
					else:
						singl = singularsk[leftw]
						newcands = set([])
						for candidate in result[key][leftp]:
							candsingl = singulars[candidate]
							newcands.add(candsingl)
						if singl not in final_substitutions.keys():
							final_substitutions[singl] = newcands
						else:
							final_substitutions[singl] = final_substitutions[singl].union(newcands)
				#If left is a verb:
				elif leftp.startswith('v'):
					for verb_tense in ['PAST_PERFECT_PARTICIPLE', 'PAST_PARTICIPLE', 'PRESENT_PARTICIPLE']:
						tensedl = verbsk[leftw][verb_tense]
						newcands = set([])
						for candidate in result[key][leftp]:
							candtensedl = verbs[candidate][verb_tense]
							newcands.add(candtensedl)
						if tensedl not in final_substitutions.keys():
							final_substitutions[tensedl] = newcands
						else:
							final_substitutions[tensedl] = final_substitutions[tensedl].union(newcands)
		return final_substitutions
		
	def getInflections(self, verbstems):
		data1 = self.mat.conjugateVerbs(verbstems, 'PAST_PERFECT_PARTICIPLE')
		data2 = self.mat.conjugateVerbs(verbstems, 'PAST_PARTICIPLE')
		data3 = self.mat.conjugateVerbs(verbstems, 'PRESENT_PARTICIPLE')
		return data1, data2, data3

	def getSingulars(self, plurstems):
		data = self.mat.inflectNouns(plurstems, 'singular')
		return data
		
	def getPlurals(self, singstems):
		data = self.mat.inflectNouns(singstems, 'plural')
		return data

	def getStems(self, sings, plurs, verbs):
		data = self.mat.lemmatizeWords(sings+plurs+verbs)
		rsings = []
		rplurs = []
		rverbs = []
		c = -1
		for sing in sings:
			c += 1
			if len(data[c])>0:
				rsings.append(data[c])
			else:
				rsings.append(sing)
		for plur in plurs:
			c += 1
			if len(data[c])>0:
				rplurs.append(data[c])
			else:
				rplurs.append(plur)
		for verb in verbs:
			c += 1
			if len(data[c])>0:
				rverbs.append(data[c])
			else:
				rverbs.append(verb)
		return rsings, rplurs, rverbs

	def getInitialSet(self, victor_corpus):
		substitutions_initial = {}
		lex = open(victor_corpus)
		for line in lex:
			data = line.strip().split('\t')
			target = data[1].strip()
			syns = wn.synsets(target)
			newline = target + '\t'
			cands = {}
			for syn in syns:
				synpos = syn.pos()
				if synpos not in cands.keys():
					cands[synpos] = set([])
				for lem in syn.lemmas():
					candidate = self.cleanLemma(lem.name())
					if len(candidate.split(' '))==1:
						cands[synpos].add(candidate)
			for pos in cands.keys():
				if target in cands[pos]:
					cands[pos].remove(target)
			if len(cands.keys())>0:
				substitutions_initial[target] = cands
		lex.close()
		return substitutions_initial

	def cleanLemma(self, lem):
		result = ''
		aux = lem.strip().split('_')
		for word in aux:
			result += word + ' '
		return result.strip()

#Class for the Biran Generator:
class BiranGenerator:

	def __init__(self, mat, complex_vocab, simple_vocab, complex_lm, simple_lm):
		"""
		Creates a BiranGenerator instance.
	
		@param mat: MorphAdornerToolkit object.
		@param complex_vocab: Path to a vocabulary of complex words.
		For more information on how to create the file, refer to the LEXenstein Manual.
		@param simple_vocab: Path to a vocabulary of simple words.
		For more information on how to create the file, refer to the LEXenstein Manual.
		@param complex_lm: Path to a language model built over complex text.
		For more information on how to create the file, refer to the LEXenstein Manual.
		@param simple_lm: Path to a language model built over simple text.
		For more information on how to create the file, refer to the LEXenstein Manual.
		"""

		self.complex_vocab = self.getVocab(complex_vocab)
		self.simple_vocab = self.getVocab(simple_vocab)
		self.complex_lm = kenlm.LanguageModel(complex_lm)
		self.simple_lm = kenlm.LanguageModel(simple_lm)
		self.mat = mat

	def getSubstitutions(self, victor_corpus):
		"""
		Generates substitutions for the target words of a corpus in VICTOR format.
	
		@param victor_corpus: Path to a corpus in the VICTOR format.
		For more information about the file's format, refer to the LEXenstein Manual.
		@return: A dictionary that assigns target complex words to sets of candidate substitutions.
		Example: substitutions['perched'] = {'sat', 'roosted'}
		"""
		
		#Get initial set of substitutions:
		print('Getting initial set of substitutions...')
		substitutions_initial = self.getInitialSet(victor_corpus)

		#Get inflected substitutions:
		print('Inflecting substitutions...')
		substitutions_inflected = self.getInflectedSet(substitutions_initial)

		#Get final substitutions:
		print('Filtering simple->complex substitutions...')
		substitutions_final = self.getFinalSet(substitutions_inflected)

		#Return final set:
		print('Finished!')
		return substitutions_final

	def getFinalSet(self, substitutions_inflected):
		#Remove simple->complex substitutions:
		substitutions_final = {}

		for key in substitutions_inflected.keys():
			candidate_list = set([])
			key_score = self.getComplexity(key, self.complex_lm, self.simple_lm)
			for cand in substitutions_inflected[key]:
				cand_score = self.getComplexity(cand, self.complex_lm, self.simple_lm)
				if key_score>=cand_score:
					candidate_list.add(cand)
			if len(candidate_list)>0:
				substitutions_final[key] = candidate_list
		return substitutions_final

	def getInflectedSet(self, result):
		final_substitutions = {}

		#Get inflections:
		allkeys = sorted(list(result.keys()))

		singulars = {}
		plurals = {}
		verbs = {}

		singularsk = {}
		pluralsk = {}
		verbsk = {}

		for i in range(0, len(allkeys)):
			key = allkeys[i]
			leftw = key

			for leftp in result[leftw].keys():
				if leftp.startswith('n'):
					if leftp=='nns':
						pluralsk[leftw] = set([])
						for subst in result[key][leftp]:
							plurals[subst] = set([])
					else:
						singularsk[leftw] = set([])
						for subst in result[key][leftp]:
							singulars[subst] = set([])
				elif leftp.startswith('v'):
					verbsk[leftw] = {}
					for subst in result[key][leftp]:
						verbs[subst] = {}

		#------------------------------------------------------------------------------------------------

		#Generate keys input:
		singkeys = sorted(list(singularsk.keys()))
		plurkeys = sorted(list(pluralsk.keys()))
		verbkeys = sorted(list(verbsk.keys()))

		#Get stems:
		singstems, plurstems, verbstems = self.getStems(singkeys, plurkeys, verbkeys)

		#Get plurals:
		singres = self.getPlurals(singstems)

		#Get singulars:
		plurres = self.getSingulars(plurstems)

		#Get verb inflections:
		verbres1, verbres2, verbres3 = self.getInflections(verbstems)

		#Add information to dictionaries:
		for i in range(0, len(singkeys)):
			k = singkeys[i]
			singre = singres[i]
			singularsk[k] = singre
		for i in range(0, len(plurkeys)):
			k = plurkeys[i]
			plurre = plurres[i]
			pluralsk[k] = plurre
		for i in range(0, len(verbkeys)):
			k = verbkeys[i]
			verbre1 = verbres1[i]
			verbre2 = verbres2[i]
			verbre3 = verbres3[i]
			verbsk[k] = {'PAST_PERFECT_PARTICIPLE': verbre1, 'PAST_PARTICIPLE': verbre2, 'PRESENT_PARTICIPLE': verbre3}

		#------------------------------------------------------------------------------------------------

		#Generate substs input:
		singkeys = sorted(list(singulars.keys()))
		plurkeys = sorted(list(plurals.keys()))
		verbkeys = sorted(list(verbs.keys()))

		#Get stems:
		singstems, plurstems, verbstems = self.getStems(singkeys, plurkeys, verbkeys)

		#Get plurals:
		singres = self.getPlurals(singstems)

		#Get singulars:
		plurres = self.getSingulars(plurstems)

		#Get verb inflections:
		verbres1, verbres2, verbres3 = self.getInflections(verbstems)

		#Add information to dictionaries:
		for i in range(0, len(singkeys)):
			k = singkeys[i]
			singre = singres[i]
			singulars[k] = singre
		for i in range(0, len(plurkeys)):
			k = plurkeys[i]
			plurre = plurres[i]
			plurals[k] = plurre
		for i in range(0, len(verbkeys)):
			k = verbkeys[i]
			verbre1 = verbres1[i]
			verbre2 = verbres2[i]
			verbre3 = verbres3[i]
			verbs[k] = {'PAST_PERFECT_PARTICIPLE': verbre1, 'PAST_PARTICIPLE': verbre2, 'PRESENT_PARTICIPLE': verbre3}

		#------------------------------------------------------------------------------------------------

		#Generate final substitution list:
		for i in range(0, len(allkeys)):
			key = allkeys[i]
			leftw = key
			for leftp in result[leftw].keys():			

				#Add final version to candidates:
				if leftw not in final_substitutions.keys():
					final_substitutions[leftw] = result[key][leftp]
				else:
					final_substitutions[leftw] = final_substitutions[leftw].union(result[key][leftp])
				#If left is a noun:
				if leftp.startswith('n'):
					#If it is a plural:
					if leftp=='nns':
						plurl = pluralsk[leftw]
						newcands = set([])
						for candidate in result[key][leftp]:
							candplurl = plurals[candidate]
							newcands.add(candplurl)
						if plurl not in final_substitutions.keys():
							final_substitutions[plurl] = newcands
						else:
							final_substitutions[plurl] = final_substitutions[plurl].union(newcands)
					#If it is singular:
					else:
						singl = singularsk[leftw]
						newcands = set([])
						for candidate in result[key][leftp]:
							candsingl = singulars[candidate]
							newcands.add(candsingl)
						if singl not in final_substitutions.keys():
							final_substitutions[singl] = newcands
						else:
							final_substitutions[singl] = final_substitutions[singl].union(newcands)
				#If left is a verb:
				elif leftp.startswith('v'):
					for verb_tense in ['PAST_PERFECT_PARTICIPLE', 'PAST_PARTICIPLE', 'PRESENT_PARTICIPLE']:
						tensedl = verbsk[leftw][verb_tense]
						newcands = set([])
						for candidate in result[key][leftp]:
							candtensedl = verbs[candidate][verb_tense]
							newcands.add(candtensedl)
						if tensedl not in final_substitutions.keys():
							final_substitutions[tensedl] = newcands
						else:
							final_substitutions[tensedl] = final_substitutions[tensedl].union(newcands)
		return final_substitutions
		
	def getInflections(self, verbstems):
		data1 = self.mat.conjugateVerbs(verbstems, 'PAST_PERFECT_PARTICIPLE')
		data2 = self.mat.conjugateVerbs(verbstems, 'PAST_PARTICIPLE')
		data3 = self.mat.conjugateVerbs(verbstems, 'PRESENT_PARTICIPLE')
		return data1, data2, data3

	def getSingulars(self, plurstems):
		data = self.mat.inflectNouns(plurstems, 'singular')
		return data
		
	def getPlurals(self, singstems):
		data = self.mat.inflectNouns(singstems, 'plural')
		return data

	def getStems(self, sings, plurs, verbs):
		data = self.mat.lemmatizeWords(sings+plurs+verbs)
		rsings = []
		rplurs = []
		rverbs = []
		c = -1
		for sing in sings:
			c += 1
			if len(data[c])>0:
				rsings.append(data[c])
			else:
				rsings.append(sing)
		for plur in plurs:
			c += 1
			if len(data[c])>0:
				rplurs.append(data[c])
			else:
				rplurs.append(plur)
		for verb in verbs:
			c += 1
			if len(data[c])>0:
				rverbs.append(data[c])
			else:
				rverbs.append(verb)
		return rsings, rplurs, rverbs

	def getComplexity(self, word, clm, slm):
		C = (clm.score(word, bos=False, eos=False))/(slm.score(word, bos=False, eos=False))
		L = float(len(word))
		return C*L

	def getInitialSet(self, victor_corpus):
		substitutions_initial = {}
		lex = open(victor_corpus)
		for line in lex:
			data = line.strip().split('\t')
			target = data[1].strip()
			if target in self.complex_vocab:
				syns = wn.synsets(target)
				newline = target + '\t'
				cands = {}
				for syn in syns:
					synpos = syn.pos()
					if synpos not in cands.keys():
						cands[synpos] = set([])
					for lem in syn.lemmas():
						candidate = self.cleanLemma(lem.name())
						if len(candidate.split(' '))==1 and candidate in self.simple_vocab:
							cands[synpos].add(candidate)
					for hyp in syn.hypernyms():
						hyppos = hyp.pos()
						if hyppos not in cands.keys():
							cands[hyppos] = set([])
						for lem in hyp.lemmas():
							candidate = self.cleanLemma(lem.name())
							if len(candidate.split(' '))==1 and candidate in self.simple_vocab:
								cands[synpos].add(candidate)
				for pos in cands.keys():
					if target in cands[pos]:
						cands[pos].remove(target)
				if len(cands.keys())>0:
					substitutions_initial[target] = cands
		lex.close()
		return substitutions_initial

	def getVocab(self, path):
		return set([line.strip() for line in open(path)])

	def cleanLemma(self, lem):
		result = ''
		aux = lem.strip().split('_')
		for word in aux:
			result += word + ' '
		return result.strip()
