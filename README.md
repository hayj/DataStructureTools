# Dependencies

	pip install orderedset

# SerializableDict

A `SerializableDict` is a Python dict which works as a "cache". It can automatically serialize your data in a pickle file or in a Mongo database. It allow you to design your program more easily by providing a dict access which automatically process the given key (or "item"). It can limit the RAM usage / disk usage by removing old / not used items in the structure.

## Installation (Python 3)

	git clone https://github.com/hayj/DataStructureTools.git
	pip install ./DataStructureTools/wm-dist/*.tar.gz

## Initialization parameters

 * **name**: The name for the pickle file or the MongoDB collection
 * **dirPath**: The directory where you want to store the pickle file
 * **funct**: A processing function which is used to process all items you want to access through `__getitem__` (e.g. `sd[key]`)
 * **useMongodb**: Set it as `True` if you want to use a MongoDB collection instead of a pickle file
 * **host**, **user** and **password**: For the Mongo database
 * **limit**: Set a size limit to the SD dict, so old / not used items will be deleted in priority
 * **cleanMaxSizeMoReadModifiedOlder**: Set a size limit in Mo
 * **cleanNotReadOrModifiedSinceNDays**: Set a day old limit
 * **cleanNotReadOrModifiedSinceNSeconds**: Set a second old limit
 * **cleanEachNAction**: This int determines the clean frequency (an action is a read / add / update)
 * **serializeEachNAction**: This int determines the serialization frequency
 * **cacheCheckRatio**: The probability an item will be re-processed to check if your program has been misdesigned (for usage of a cache which is supposed to return always same values)
 * **raiseBadDesignException**: Set it as `False` if you want an logged error instead of an Exception in the case you misdesigned your Python script
 * **readAndAddOnly**: Set this init param as `True` if you don't want to update any item
 * **logger**: A logger from `systemtools.logger` (see [SystemTools](https://github.com/hayj/SystemTools))
 * **verbose**: To set the verbose (`True` or `False`)

## Tutorial

### The default usage

With default parameters, a SD works the same as a Python dict:

	>>> from datastructuretools.hashmap import SerializableDict
	>>> sd = SerializableDict()
	>>> sd["a"] = 1

But it retains each get / add / update timestamps in a private dict structure:

	>>> print(sd.data)
	{'a': {'read': 1522590582.0, 'modified': 1522590582.0, 'modifiedCount': 0, 'readCount': 0, 'created': 1522590582.0, 'value': 1}}

The main difference from a Python dict is that it doesn't throw any Exception using `del` or `__getitem__`:

	>>> print(sd["a"])
	1
	>>> del sd["a"]
	>>> print(sd["a"])
	None
	>>> del sd["a"]

### Use it as a cache and limit the RAM usage

Now, for example, imagine you have a lot of strings (say more than your RAM can store) to convert in lower case (or a function which requires more computing time). We define the function:

	>>> def strToLower(text):
	...     if text is None:
	...             return None
	...     return text.lower()

You can init a SD with a specific limit, so you're sure it will not go over ~100 items:

	>>> sd = SerializableDict(limit=100)

Now each time you receive a new string (from outside), you can use SD as a cache:

	>>> def compute(text):
	...     if text in sd
	...             return sd[text]
	...     else:
	...             result = strToLower(text)
	...             sd[text] = result
	...             return result

So in case you receive same strings several times, you don't re-compute `strToLower`. The SD structure will keep fresh computed items and automatically remove old items. The items that are most often received will be kept in priority (according to read, modified and created timestamps).

If you want to set the clean frequency, you can use `cleanEachNAction` init param (`500` is the default):

	>>> sd = SerializableDict(limit=100, cleanEachNAction=500)

Here olds items will be removed each 500 actions (read, add, update).

### But coding this way is a little bit boring

In the example above, we need to check if the lowered text exists (which mean we need to check if it was already computed). So we introduced the possibility of giving a function in parameters which will work as the processing function for each item in the structure. You just need to give a defined function in `funct` init param. Now each access of an item in the SD will automatically compute it OR return the already computed one. Now the `compute` function is drastically reduced:

	>>> sd = SerializableDict(funct=strToLower, limit=100)
	>>> def compute(text):
	...     return sd[text]

And we don't even have to define the `compute` function but use `sd` directly...

If your processing funct (`strToLower` in our case) have extra parameters (say a boolean `toStrip=True`), instead of doing `sd[text]` you can use the get class method this way (with `*args, **kwargs`):

	>>> sd.get(text, toStrip=False)

The benefit of this feature is that you can design you program a way you don't care about existing items, you simply use the `sd` cache always like the processed result of the item exists.


### Serialize your data

The next feature of `SerializableDict` is that you can serialize `sd` in a zipped pickle file so you don't loose any "item result" across several executions of your script. It is useful in the case you compute features in a machine learning task for example.

You need to set init params `name` and optionally `dirPath` (default is `~/tmp/SerializableDicts`):

	>>> sd = SerializableDict(name="lowered_texts", funct=strToLower)

And you can set `serializeEachNAction` as `500` (default) so `sd` will save your data in `~/tmp/SerializableDicts/lowered_texts.pickle.zip` each `500` actions. Optionally you can use the init param `compresslevel` of the `gzip` lib.

When your program ends, you can manually save `sd`:

	>>> sd.save()

You can also reset the data (and remove the pickle file) using:

	>>> sd.reset()

### Do not misdesign your programs

The counterpart of these 2 features described above (using the `funct` init param) is you can misdesign your program and return an old "item result" (the processing of the item) which is not a right one according to you actual program version. In our case, for example, imagine you updated the `strToLower` function so it doesn't lower the first letter of the text, you may not realize that your `sd` return bad "item results" because it return old ones loaded from the pickle file.

So to be sure to do not misdesign your program, you can set the init param `cacheCheckRatio`. It enable the re-computation of an item even it already exists. `cacheCheckRatio` is the probability to re-compute an item at each action. If you misdesigned your program (i.e. the new value is different from the old one in the SD), it will throw an `Exception` or just log an error if you set the init param `raiseBadDesignException` as `False`.

	>>> sd = SerializableDict(funct=strToLower, limit=100, cacheCheckRatio=0.1)

If you set the `cacheCheckRatio` probability to `0.1`, you will loose ~10% computation time but you will be sure you didn't misdesign your script. You can re-set it to `0.0` when you finish all tests.

### Serialization through a MongoDB collection

If you need to centralize your data in the case you have several servers, or several process, or if you want to take benefit of MongoDB in its indexing capability, you can set `useMongodb` as `True` and give `host`, `user` and `password`:

	>>> sd = SerializableDict(name="mycollection", useMongodb=True,
	            host="localhost", user=None, password=None) # Default

All other features work the same except it does not serialize each n actions but insert each item and "item result" in the MongoDB collection `mycollection` in the database `serializabledicts`. It use an index on the SD key to works the same as a Python dict.

If you are on Ubuntu, I recommend to follow this tutorial if you want to install MongoDB on localhost : <https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/>. Or you can open the database and secure it: <https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-mongodb-on-ubuntu-16-04>.

You can store your MongoDB password in a secure folder like `~/.ssh` to load it in your Python script.

### Set a deadline

For example, in the case you have to download a web page in your script but you don't want to request the server each time you execute your script, you can set a deprecation of your data when they have 10 days old using `cleanNotReadOrModifiedSinceNDays`:

	>>> sd = SerializableDict(name="my_downloaded_data",
			cleanNotReadOrModifiedSinceNDays=10, funct=downloadMyData)

So all items which were read / add / modified (take the most recent one) more than 10 days will be remove and a `get` action on your SD will re-download the data. You can also use `cleanNotReadOrModifiedSinceNSeconds`. Read `BashScripts` below for a concrete example.

## Examples

### Unit tests

You can see [unit tests](https://github.com/hayj/DataStructureTools/blob/master/datastructuretools/test/hashmap.py) which shows a more in-depth usage of SD.

### Unshortener

The [Unshortener class](https://github.com/hayj/Unshortener/blob/master/unshortener/unshortener.py) use a SD to store unshortened urls (like `http://bit.ly/...`) in a Mongo database. It use a limit of 10M urls.

### DomainDuplicate

In [DomainDuplicate class](https://github.com/hayj/DomainDuplicate/blob/master/domainduplicate/domainduplicate.py) we use a SD to store duplicates in a Mongo database. The key is a md5 hash of the title, the text and the domain of a web page, and each time we found the same hash on an other url, we store the url in the "item result" (which is a list) of this hash key in the SD.

### LangRecognizer

In [LangRecognizer](https://github.com/hayj/NLPTools/blob/master/nlptools/langrecognizer.py) we use a SD to do not re-compute text for which we already recognized the lang. It allow the user of this library to do not take care of the computation time of the NLP function in the case he already ask the lang of a text.

### A cache for bash scripts

[The BashScripts class](https://github.com/hayj/DataTools/blob/master/datatools/bashscripts.py) use a SD to download and cache GitHub bash scripts and reload these script each 10 days from <https://github.com/hayj/Bash>.

### Scraping

In a project we use SD to scrap html using `BeautifulSoup`. Each 2 seconds during the scroll of a webpage (using Selenium), we rescrap all `ul > li` in the page, all already scraped `li` are not re-computed, we use a limit of 1000 without any serialization. The SD allow us to design our scraping / scroll process using simple `for` loops and allow us to quickly rescrap html data without having to code a cache mechanism.

In this project, the key is a html string and the "item result" is a Python dict which represent data scraped from the html of the `li` element. We use a `cacheCheckRatio` of `0.01`.

### Crawling

In another project which implies the crawling of urls, we use SD to retain which urls failed, so we can share failed across several servers using the MongoDB support of SD to don't re-crawl these urls.
