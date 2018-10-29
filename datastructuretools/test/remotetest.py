from datastructuretools.hashmap import *
from datastructuretools import config as dstConfig
dstConfig.sdUser = "student"
dstConfig.sdPassword = "cs-lri-octopeek-984135584714323587326" # Or load it from a file in a secure folder like ".ssh"
dstConfig.sdDatabaseName = "student"
sd = SerializableDict("sdtest", useMongodb=True, host="212.129.44.40")
sd["a"] = 1
print(sd["a"])