

import copy

# class Trie:


class Trie:
	"""
		You can add terms, a term is a Trie node which is a termination (for exemple, if your Trie is
		based on chars, adding the term "test" will add a termination on
		theTrie["t"]["e"]["s"]["t"], so theTrie["t"]["e"]["s"]["t"].isTerm() will be True,
		but theTrie["t"]["e"]["s"].isTerm() will return False)
		You can also add child, for exemple: theTrie.addChild(list("tes"))
		Then add a term: theTrie.addTerm(list("test"))
		Or you can do theTrie.addChild(list("tes")) the theTrie.getChild(list("tes")).addTerm("t")
	"""
	def __init__(self, isTerm=False):
		self.__isTerm = isTerm
		self.children = dict()

	def setIsTerm(self, isTerm):
		self.__isTerm = isTerm

	def setChildren(self, children):
		self.children = children

	def addTerm(self, dataList):
		if not isinstance(dataList, list):
			dataList = [dataList]
		self.addChild(dataList)
		self.getChild(dataList).setIsTerm(True)

	def getChild(self, dataList):
		if not isinstance(dataList, list):
			dataList = [dataList]
		if len(dataList) == 0:
			return self
		try:
			return self.children[dataList[0]].getChild(dataList[1:])
		except:
			return None

	def isTerm(self):
		return self.__isTerm

	def hasChild(self, *args, **kwargs):
		return self.getChild(*args, **kwargs) is not None

	def addChild(self, dataList):
		if not isinstance(dataList, list):
			dataList = [dataList]
		if len(dataList) > 0:
			currentChild = dataList[0]
			nextChildren = dataList[1:]
			if currentChild not in self.children:
				t = Trie()
				self.children[currentChild] = t
			self.children[currentChild].addChild(nextChildren)

	def termMaxLength(self):
		currentMax = None
		if len(self.children) > 0:
			for data, child in self.children.items():
				childMaxLength = child.termMaxLength()
				if childMaxLength is not None and (currentMax is None or childMaxLength > currentMax):
					currentMax = childMaxLength
		if currentMax is not None:
			return 1 + currentMax
		elif self.isTerm():
			return 0
		else:
			return None

	def __getitem__(self, data):
		return self.children[data]

	def hasTerm(self, dataList):
		if dataList is None:
			dataList = []
		if not isinstance(dataList, list):
			dataList = [dataList]
		if len(dataList) == 0:
			return self.__isTerm
		try:
			return self.children[dataList[0]].hasTerm(dataList[1:])
		except:
			return False

	def __repr__(self):
		text = ""
		for data, child in self.children.items():
			childrenRepr = repr(child)
			childrenRepr = childrenRepr.replace("\n", "\n\t")
			text += str(data)
			if child.isTerm():
				text += " <--"
			if childrenRepr != "":
				text += "\n\t"
				text += childrenRepr
			text += "\n"
		if text != "":
			text = text[:-1]
		return text

	def findLongestTerm(self, tokens):
		"""
			This function return the longer sequence of tokens
			the trie can found starting by the first element
			of tokens
			It returns None in nothing was found
		"""
		if tokens is None:
			return None
		maxLength = self.termMaxLength()
		longest = None
		currentTrie = self
		alreadyPassed = []
		for token in tokens:
			if len(alreadyPassed) < maxLength and currentTrie.hasChild(token) :
				currentTrie = currentTrie.getChild(token)
				alreadyPassed.append(token)
				if currentTrie.isTerm():
					longest = copy.copy(alreadyPassed)
			else:
				break
		return longest



	def searchTermIn(self, text, maxTokens=None):
		"""
			This function will search any token from the trie structure
			if the text starting from each char of the text
		"""
		if text is None:
			return None
		foundTokens = []
		for index in range(len(text)):
			currentText = text[index:]
			longest = self.findLongestTerm(currentText)
			if longest is not None:
				foundTokens.append(longest)
			if maxTokens is not None and len(foundTokens) >= maxTokens:
				break
		return foundTokens

	def hasTermIn(self, *args, **kwargs):
		result = self.searchTermIn(*args, maxTokens=1, **kwargs)
		if result is None or len(result) == 0:
			return False
		return True


def makeTrie(iterable, doSpaceSplit=False, doStrSplit=False):
	t = Trie()
	for current in iterable:
		if doStrSplit and isinstance(current, str):
			current = list(current)
		if doSpaceSplit:
			t.addTerm(current.split(" "))
		else:
			t.addTerm(current)
	return t

def test1():
	t = Trie()
	print(t.termMaxLength())
	t.addTerm(["ccc"])
	print(t.termMaxLength())
	exit()
	t.addChild("aaa")
	t.addChild("bbb")
	t["bbb"].setIsTerm(True)
	t["aaa"].addTerm(["ccc"])
	t["aaa"].addChild("ddd")
	t["bbb"].addChild("eee")
	t["bbb"].addChild(["fff", "zzz", "iii"])
	t["bbb"]["eee"].addChild(["rrr", "ttt"])
	t["bbb"]["eee"]["rrr"].addChild("ooo")
	t["bbb"]["eee"]["rrr"].addChild("ppp")

	t["bbb"]["eee"].addTerm(["rrr"])
	t["bbb"]["fff"].addChild(["rrr", "iii", "iii", "iii", "iii", "iii"])
	t["bbb"]["fff"]["rrr"]["iii"]["iii"].setIsTerm(True)
	t["bbb"]["fff"].addTerm(["rrr"])
	t["bbb"]["fff"].setIsTerm(True)
	t["bbb"]["fff"]["zzz"].setIsTerm(True)

	print(t)
	print(t.termMaxLength())

	print(t.findLongestTerm(["bbb", "eee"]))


	# assert t.hasTerm("aaa") == False
	# assert t.hasTerm(None) == False
	# assert t.hasTerm("bbb") == True
	# assert t.hasTerm(["rrr", "iii"]) == False
	# assert t.hasTerm(["bbb", "fff", "zzz", "iii"]) == False
	# assert t.hasTerm(["bbb", "fff", "rrr"]) == False

def test2():
	t = Trie()
	text = "my name namoris isi norty"
	words = text.split()
	t = Trie()
	for word in words:
		chars = list(word)
		t.addTerm(chars)
	print(t)
	print(t.hasTermIn("op yyy namorisaa ttt"))
def test3():
	t = Trie()
	text = "my name namoris isi norty"
	words = text.split()
	t = Trie()
	for word in words:
		chars = list(word)
		t.addTerm(chars)
	print(t)
	print(t.hasTermIn("op yyy namorisaa ttt"))

if __name__ == '__main__':
	test2()