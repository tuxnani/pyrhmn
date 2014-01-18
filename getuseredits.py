import json
import urllib2

data = json.load(urllib2.urlopen('http://te.wikipedia.org/w/api.php?action=userdailycontribs&format=json&user=%E0%B0%B0%E0%B0%B9%E0%B1%8D%E0%B0%AE%E0%B0%BE%E0%B0%A8%E0%B1%81%E0%B0%A6%E0%B1%8D%E0%B0%A6%E0%B1%80%E0%B0%A8%E0%B1%8D&daysago=10'))
print (data)
pprint(data)
