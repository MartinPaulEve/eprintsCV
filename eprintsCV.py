#!/usr/bin/env python
# A script that downloads a publication list from eprints and formats it for display on an academic website/web CV
# Copyright Martin Paul Eve 2014

"""eprintsCV: a script that downloads a publication list from eprints and formats it for display on an academic website/web CV

Usage:
    eprintsCV.py <eprints_location> <eprints_user> <list_of_types>
    eprintsCV.py (-h | --help)
    eprintsCV.py --version

Options:

    -h --help  Show this screen.
    --version  Show version.
"""

from docopt import docopt
import urllib2
import json
from datetime import datetime

def printableHeading(x):
	return {
		'book': "Books",
		'article': "Journal Articles",
	}[x]

def printHeading(heading):
	print str.format("<h1>{0}</h1>", printableHeading(heading))


def printItem(item, eprint_url):
	# generate the creators list
	creators = ""
	
	for creator in item['creators']:
		if creators <> "":
			creators = creators + ", "

		if creator['id'] is not None:
			creators = creators + str.format('<a href="{0}view/creators/{3}.html">{1}, {2}</a>', eprint_url, creator['name']['family'].encode('utf8'), creator['name']['given'].encode('utf8'), creator['id'])
		else:
			creators = creators + str.format('{0}, {1}', creator['name']['family'].encode('utf8'), creator['name']['given'].encode('utf8'))

	if item['type'] == 'book':
		print str.format('<p>{0}, <a href="{4}"><i>{1}</i></a> ({2}: {3})</p>', creators, item['title'].encode('utf8'), item['publisher'].encode('utf8'), datetime.strptime(item['date'][0:4], "%Y").year, item['uri'])

	if item['type'] == "article":
		# build the volume/number format
		volume = ""

		if 'volume' in item:
			volume = ", "
			volume = str(item['volume'])

		if 'number' in item:
			if 'volume' in item:
				volume = ", "
			volume = volume + str.format("({0})", str(item['number']))

		print str.format('<p>{0}, "<a href="{5}">{1}</a>", <i>{2}</i>{3}, {4}</p>', creators, item['title'].encode('utf8'), item['publication'].encode('utf8'), volume, datetime.strptime(item['date'][0:4], "%Y").year, item['uri'])

def main():
	# read  command line arguments
	args = docopt(__doc__, version='eprintsCV 0.1')
	
	# build the repository path
	repo = args['<eprints_location>']

	if not(repo.startswith("htt")):
		repo = "http://" + repo

	if not(repo.endswith("/")):
		repo = repo + "/"

	url = repo + "cgi/exportview/creators/" + args['<eprints_user>'] + "/JSON/" + args['<eprints_user>'] + ".js"

	# download the JSON version
	response = urllib2.urlopen(url)
	jsonData = response.read()

	# decode the JSON object into a list of dictionaries
	# NB that, helpfully, this list is by default reverse sorted (newest first)
	# should this ever change, it would need a lamda sort:
	# jsonSorted = sorted(list_to_be_sorted, key=lambda k: k['date']) 
	jsonList = json.loads(jsonData)

	for currentType in args['<list_of_types>'].split(","):
		# display a heading
		printHeading(currentType)
		for currentItem in jsonList:
			if currentItem['type'] == currentType:
				# this is an item of that type
				printItem(currentItem, repo)


if __name__ == '__main__':
    main()
