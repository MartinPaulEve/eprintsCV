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


def print_start():
    print "<ul>"


def print_end():
    print "</ul>"


def printable_heading(x):
    return {
        'book': "Books",
        'article': "Journal Articles",
        'book_section': "Book Chapters",
        'conference_item': "Conference Papers/Events",
    }[x]


def print_heading(heading):
    print str.format("<h1>{0}</h1>", printable_heading(heading))


def print_item(item, eprint_url):
    # generate the creators list
    creators = ""

    for creator in item['creators']:
        if creators <> "":
            creators += ", "

        if creator['id'] is not None:
            creators += str.format('<a href="{0}view/creators/{3}.html">{1}, {2}</a>', eprint_url,
                                   creator['name']['family'].encode('utf8'),
                                   creator['name']['given'].encode('utf8'), creator['id'])
        else:
            creators += str.format('{0}, {1}', creator['name']['family'].encode('utf8'),
                                   creator['name']['given'].encode('utf8'))

    if item['type'] == 'book':
        print '<li>{0}, <a href="{4}"><i>{1}</i></a> ({2}: {3})</li>'.format(creators,
                                                                             item['title'].encode('utf8'),
                                                                             item['publisher'].encode('utf8'),
                                                                             datetime.strptime(item['datestamp'][0:4],
                                                                                               "%Y").year,
                                                                             item['uri'])

    if item['type'] == "article":
        # build the volume/number format
        volume = ""

        if 'volume' in item and not 'number' in item:
            volume = ' ({0})'.format(str(item['volume']))
        elif 'number' in item and not 'volume' in item:
            volume = ' {0}'.format(str(item['number']))
        elif 'number' in item and 'volume' in item:
            volume = ' {0}({1})'.format(str(item['volume']), str(item['number']))

        print '<li>{0}, "<a href="{5}">{1}</a>", <i>{2}</i>{3}, {4}</li>'.format(creators,
                                                                                 item['title'].encode('utf8'),
                                                                                 item['publication'].encode('utf8'),
                                                                                 volume,
                                                                                 datetime.strptime(
                                                                                     item['datestamp'][0:4], "%Y").year,
                                                                                 item['uri'])

    if item['type'] == "book_section":
    # generate the editors list
        editors = ""

        if 'editors' in item:
            for editor in item['editors']:
                if editors == "":
                    editors = ", ed. by "
                if editors != ", ed. by ":
                    editors += editors + ", "

            editors = editors + '{0}, {1}'.format(editor['name']['family'].encode('utf8'),
                                                  editor['name']['given'].encode('utf8'))

        print '<li>{0}, "<a href="{6}">{1}</a>", in <i>{2}</i>{3} ({4}: {5})</li>'.format(creators,
                                                                                          item['title'].encode(
                                                                                              'utf8'),
                                                                                          item['book_title'].encode(
                                                                                              'utf8'),
                                                                                          editors,
                                                                                          item['publisher'].encode(
                                                                                              'utf8'),
                                                                                          datetime.strptime(
                                                                                              item['datestamp'][0:4],
                                                                                              "%Y").year,
                                                                                          item['uri'])

    if item['type'] == "conference_item":
        print ('<li>{0}, "<a href="{4}">{1}</a>", <i>{2}</i> {3}</li>'.format(creators,
                                                                              item['title'].encode('utf8'),
                                                                              item['event_title'].encode('utf8'),
                                                                              datetime.strptime(item['datestamp'][0:4],
                                                                                                "%Y").year,
                                                                              item['uri']))


def main():
    # read  command line arguments
    args = docopt(__doc__, version='eprintsCV 0.1')

    # build the repository path
    repo = args['<eprints_location>']

    if not (repo.startswith("htt")):
        repo = "http://" + repo

    if not (repo.endswith("/")):
        repo += "/"

    url = repo + "cgi/exportview/people/" + args['<eprints_user>'] + "/JSON/" + args['<eprints_user>'] + ".js"

    # download the JSON version
    response = urllib2.urlopen(url)
    json_data = response.read()

    # decode the JSON object into a list of dictionaries
    # NB that, helpfully, this list is by default reverse sorted (newest first)
    # should this ever change, it would need a lamda sort:
    # jsonSorted = sorted(list_to_be_sorted, key=lambda k: k['date'])
    json_list = json.loads(json_data)

    for currentType in args['<list_of_types>'].split(","):
        # display a heading
        print_heading(currentType)
        print_start()
        for currentItem in json_list:
            if currentItem['type'] == currentType:
                # this is an item of that type
                print_item(currentItem, repo)
        print_end()


if __name__ == '__main__':
    main()
