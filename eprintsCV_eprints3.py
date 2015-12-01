#!/usr/bin/env python
# A script that downloads a publication list from eprints and formats it for display on an academic website/web CV
# Copyright Martin Paul Eve 2014

"""eprintsCV: a script that downloads a publication list from eprints and formats it for display on an academic website/web CV

Usage:
    eprintsCV.py <eprints_location> <eprints_user> <list_of_types> [--dump]
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
        'book_ned': "Books",
        'book_ed': "Edited Volumes",
        'article_ref': "Articles in Peer-Reviewed Journals",
        'article_ref_nev': "Articles in Peer-Reviewed Journals",
        'article_nef_nev': "Other Articles",
        'article_nev': "Other Articles",
        'article': "Articles",
        'article_rev': "Reviews",
        'book_section': "Book Chapters",
        'conference_item': "Conference Papers/Events",
    }[x]


def print_heading(heading):
    print str.format("<h1>{0}</h1>", printable_heading(heading))


def print_item(item, eprint_url):
    # generate the creators list
    creators = ""
    editors = ""

    for creator in item['creators'][:-1]:
        if creators <> "":
            creators += ", "

        creators += str.format('{0}, {1}', creator['name']['family'].encode('utf8'), creator['name']['given'].encode('utf8'))

    if creators <> "":
        creators += ", and "

    creator = item['creators'][-1]

    creators += str.format('{0}, {1}', creator['name']['family'].encode('utf8'), creator['name']['given'].encode('utf8'))

    if 'editors' in item:
      for editor in item['editors'][:-1]:
        if editors == "":
          editors = ", ed. by "
        if editors != ", ed. by ":
          editors += ", "

        editors += str.format('{0}, {1}', editor['name']['family'].encode('utf8'), editor['name']['given'].encode('utf8'))

      if editors == "":
          editors = ", ed. by "
      if editors != ", ed. by ":
        editors += ", and "

      editor = item['editors'][-1]

      editors += str.format('{0}, {1}', editor['name']['family'].encode('utf8'), editor['name']['given'].encode('utf8'))

    try:
        the_date = datetime.strptime(item['date'][0:4], "%Y").year
    except:
        the_date = "n.d."

    if item['type'] == 'book':
        print '<li>{0}, <a href="{4}"><i>{1}</i></a>{5} ({2}: {3})</li>'.format(creators,
                                                                                 item['title'].encode('utf8'),
                                                                                 item['publisher'].encode('utf8'),
                                                                                 the_date,
                                                                                 item['uri'],
                                                                                 editors)
    

    if item['type'] == "article":
        # build the volume/number format
        volume = ""

        if 'volume' in item and not 'number' in item:
            volume = ' ({0})'.format(str(item['volume']))
        elif 'number' in item and not 'volume' in item:
            volume = ' {0}'.format(str(item['number']))
        elif 'number' in item and 'volume' in item:
            volume = ' {0}({1})'.format(str(item['volume']), str(item['number']))

        print '<li>{0}, &ldquo;<a href="{5}">{1}</a>&rdquo;, <i>{2}</i>{3}, {4}</li>'.format(creators,
                                                                                 item['title'].encode('utf8'),
                                                                                 item['publication'].encode('utf8'),
                                                                                 volume,
                                                                                 the_date,
                                                                                 item['uri'])

    if item['type'] == "book_section":
        print '<li>{0}, &ldquo;<a href="{6}">{1}</a>&rdquo;, in <i>{2}</i>{3} ({4}: {5})</li>'.format(creators,
                                                                                          item['title'].encode(
                                                                                              'utf8'),
                                                                                          item['book_title'].encode(
                                                                                              'utf8'),
                                                                                          editors,
                                                                                          item['publisher'].encode(
                                                                                              'utf8'),
                                                                                          the_date,
                                                                                          item['uri'])

    if item['type'] == "conference_item":
        print ('<li>{0}, &ldquo;<a href="{5}">{1}</a>&rdquo;, <i>{2}</i>, {4}, {3}</li>'.format(creators,
                                                                              item['title'].encode('utf8'),
                                                                              item['event_title'].encode('utf8'),
                                                                              the_date,
                                                                              item['event_location'],
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

    if args['--dump']:
        print json_list
        return

    for currentType in args['<list_of_types>'].split(","):
        # display a heading
        print_heading(currentType)

        do_print = False

        rev = "ANY"

        if currentType.endswith("_rev"):
          rev = 'TRUE'
          currentType = currentType[0:-4]
        elif currentType.endswith("_nev"):
          rev = 'FALSE'
          currentType = currentType[0:-4]

        needs_ref = "ANY"
        
        if currentType.endswith("_ref"):
          needs_ref = 'TRUE'
          currentType = currentType[0:-4]
        elif currentType.endswith("_nef"):
          needs_ref = 'FALSE'
          currentType = currentType[0:-4]

        ed = "ANY"

        if currentType.endswith("_ed"):
          ed = 'TRUE'
          currentType = currentType[0:-3]
        elif currentType.endswith("_ned"):
          ed = 'FALSE'
          currentType = currentType[0:-4]        

        print_start()
        for currentItem in json_list:
            if currentItem['type'] == currentType:
              if needs_ref == "ANY":
                do_print = True
              elif needs_ref <> "ANY" and 'refereed' in currentItem and currentItem['refereed'] == needs_ref:
                # this is an item of that type
                do_print = True
              else:
                do_print = False

              if do_print:
                if rev == "ANY":
                  do_print = True
                elif rev == "TRUE" and currentItem['title'].encode('utf8').startswith("Review of"):
                  do_print = True
                elif rev == "FALSE" and currentItem['title'].encode('utf8').startswith("Review of") == False:
                  do_print = True
                else:
                  do_print = False

              if do_print:
                if ed == "ANY":
                  do_print = True
                elif ed == "TRUE" and 'editors' in currentItem:
                  # this is an item of that type
                  do_print = True
                elif ed == "FALSE" and not 'editors' in currentItem:
                  # this is an item of that type
                  do_print = True
                else:
                  do_print = False

              if do_print:
                print_item(currentItem, repo)

        print_end()


if __name__ == '__main__':
    main()
