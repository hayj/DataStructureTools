
from systemtools.basics import *
from systemtools.duration import *
from systemtools.printer import *
from threading import Lock


class Cache:
	"""
		A dict-like class that periodicaly clean values that receive less actions (read / write). It remove values randomly among those having less actions until reaching a certain amount of free RAM. The cleaning process is a background thread that check the free RAM each 0.5 sec by default.

		When using a Cache instance, don't forget to purge it (using `purge()` which stop the intern timer or using the with statement) because the timer that launch the periodic cleaning will keep a reference of the instance, thus the garbage collector won't remove the instance from RAM.
	"""
	def __init__\
	(
		self,
		getter,
		name=None,
		minFreeRAM=2.0,
		cleanInterval=0.5,
		cleanRatio=1/100,
		logger=None,
		verbose=True,
	):
		# We get params:
		self.logger = logger
		self.verbose = verbose
		self.getter = getter
		self.name = name
		self.minFreeRAM = minFreeRAM
		self.cleanInterval = cleanInterval
		self.cleanRatio = cleanRatio
		# We init all data:
		self.purged = False
		self.data = dict()
		self.actionCount = dict()
		self.countIndex = {1: set()}
		# We init the timer that will clean data each n seconds:
		self.lock = Lock()
		self.timer = Timer(self.__clean, self.cleanInterval, sleepFirst=True)
		self.start()
	
	def assertNotPurged(self):
		if self.purged:
			raise Exception("The cache was purged, you cannot use it anymore.")

	def start(self):
		self.timer.start()
	def __enter__(self):
		return self

	def stop(self):
		self.purge()
	def __del__ (self):
		self.purge()
	def purge(self):
		"""
			Purges the data and stop the periodic cleaning.

			See https://stackoverflow.com/questions/1481488/what-is-the-del-method-how-to-call-it/2452895
			And https://stackoverflow.com/questions/1984325/explaining-pythons-enter-and-exit
			The timer keep a ref of self, we need to stop it so th gc can collect the instance.
			So we use either the __init__ and `stop` or the with statment

			A good solution would be to just stop the timer instead of setting `self.data` to None, but after many test in a notebook, the garbage collector do not free the RAM (afetr a `c.purge() ; del c` or using the with statement) until we try to access to the instance `c` and getting a None exception... don't know why...
			Probably du to the timer... a solution would be to don't use a timer but cleaning at each set or get...
		"""
		self.timer.stop()
		self.data = None
		self.purged = True
	def __exit__ (self, type, value, tb):
		self.purge()

	def __contains__(self, key):
		"""
			Check if a key exists in data. Can return False in case the value was removed.
		"""
		return key in self.data

	def __delitem__(self, key):
		"""
			Delete a single key) from the cache, can raise KeyError.
		"""
		# if key not in self.actionCount:
		# 	raise KeyError()
		# if key in self.data:
		del self.data[key]

	def remove(self, keys):
		"""
			Safely (no error) delete keys (or a single key) from the cache (if not already removed).
		"""
		with self.lock:
			if not isinstance(keys, list):
				keys = [keys]
			for key  in keys:
				if key in self.data:
					del self.data[key]

	def __getitem__(self, key):
		"""
			Returns an item by its key. Use `get(key, *args, **kwargs)` to give args that will be used by the getter function.
		"""
		return self.get(key)

	def __getterKwargs(self, kwargs):
		if 'logger' not in kwargs:
			kwargs['logger'] = self.logger
		if 'verbose' not in kwargs:
			kwargs['verbose'] = self.verbose
		return kwargs

	def get(self, key, *args, **kwargs):
		"""
			Returns the value corresponding to the key given. It will use the getter function if the key was not already loaded or was delete by the periodic clean.
		"""
		with self.lock:
			self.assertNotPurged()
			if key in self.data:
				value = self.data[key]
			else:
				value = self.getter(key, *args, **self.__getterKwargs(kwargs))
				self.data[key] = value
			self.__action(key)
			return self.data[key]

	def __setitem__(self, key, value):
		with self.lock:
			self.assertNotPurged()
			self.data[key] = value
			self.__action(key)

	def __len__(self):
		"""
			Returns the length of the actual data (values could be removed by the periodic clean).
		"""
		self.assertNotPurged()
		return len(self.data)

	def items(self):
		self.assertNotPurged()
		return self.data.items()

	def keys(self):
		self.assertNotPurged()
		return self.data.keys()

	def __action(self, key):
		if key not in self.actionCount:
			self.actionCount[key] = 0
		self.actionCount[key] += 1
		currentActionCount = self.actionCount[key]
		previousActionCount = currentActionCount - 1
		if previousActionCount > 0:
			self.countIndex[previousActionCount].remove(key)
		if currentActionCount not in self.countIndex:
			self.countIndex[currentActionCount] = set()
		self.countIndex[currentActionCount].add(key)

	def __minaction(self):
		for i in range(len(self.countIndex)):
			currentCount = i + 1
			if len(self.countIndex[currentCount]) > 0:
				keys = [key for key in self.countIndex[currentCount] if key in self.data]
				if len(keys) > 0:
					return keys

	def __clean(self):
		"""
			Clean 1% of data iteratively until reaching minFreeRAM
		"""
		with self.lock:
			if not self.purged:
				cleanCount = 0
				while freeRAM() < self.minFreeRAM:
					toRemove = self.__minaction()
					if toRemove is None or len(toRemove) == 0:
						break
					else:
						index = int(self.cleanRatio * len(self.data))
						if index == 0:
							index = 1
						toRemove = shuffle(toRemove)[:index]
						for key in toRemove:
							del self.data[key]
							cleanCount += 1
				if cleanCount > 0:
					if self.name is not None:
						message = str(cleanCount) + " values cleaned from " + self.name
					else:
						message = str(cleanCount) + " values cleaned from " + str(self)
					logWarning(message, self)

	def printState(self):
		self.assertNotPurged()
		log("Keys: " + b(self.data.keys(), 4) + " (" + str(len(self)) + ")", self)
		log("Count index: " + b(self.countIndex, 4), self)
		log("Action count: " + b(self.actionCount, 4), self)