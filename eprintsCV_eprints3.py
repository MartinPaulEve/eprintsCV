#!/usr/bin/env python3
# coding=UTF-8
# A script that downloads a publication list from eprints and formats it for display on an academic website/web CV
# Copyright Martin Paul Eve 2016
# Requires python3

"""eprintsCV: a script that downloads a publication list from eprints and formats it for display on an academic website/web CV

Usage:
    eprintsCV.py <eprints_location> <eprints_user> <list_of_types> [--dump]
    eprintsCV.py (-h | --help)
    eprintsCV.py --version

Options:

    -h --help  Show this screen.
    --version  Show version.
"""

import json
from datetime import datetime
from urllib.request import urlopen

from docopt import docopt

schemaids = {"Martin Paul Eve": 'itemid="https://www.martineve.com"'}


def print_start():
    print("<ul>")


def print_end():
    print("</ul>")


def printable_heading(x):
    return {
        'book': "Books",
        'book_ned': "Books",
        'book_ed': "Edited Volumes",
        'article_ref': "Journal Articles",
        'article_ref_nev': "Journal Articles",
        'article_nef_nev': "Other Articles",
        'article_nev': "Other Articles",
        'article': "Articles",
        'article_rev': "Reviews",
        'book_section': "Book Chapters",
        'conference_item': "Conference Papers/Events",
    }[x]


def print_heading(heading):
    print (str.format("<h4>{0}</h4>", printable_heading(heading)))


def print_item(item, eprint_url):
    # generate the creators list
    creators = ""
    editors = ""
    schemaid = ""

    for creator in item['creators'][:-1]:
        if creators != "":
            creators += ", "

        lookup = creator['name']['given'] + " " + creator['name']['family']

        shouldcreate = False

        if lookup in schemaids:
            schemaid = schemaids[lookup]
        else:
            schemaids[lookup] = 'itemid="https://www.martineve.com/' + creator['name']['given'] + \
                                creator['name']['family'] + '"'
            schemaid = schemaids[lookup]
            shouldcreate = True

        if shouldcreate:
            creators += str.format(
                '<span itemtype="http://schema.org/Person" itemscope {2} itempropreplace><span itemprop="name"><span itemprop="familyName">{0}</span>, <span itemprop="givenName">{1}</span></span></span>',
                creator['name']['family'], creator['name']['given'], schemaid)
        else:
            creators += str.format(
                '<span itemtype="http://schema.org/Person" itemscope {2} itempropreplace>{0}, {1}</span>',
                creator['name']['family'], creator['name']['given'], schemaid)

    if creators != "":
        creators += ", and "

    creator = item['creators'][-1]

    lookup = creator['name']['given'] + " " + creator['name']['family']

    shouldcreate = False

    if lookup in schemaids:
        schemaid = schemaids[lookup]
    else:
        schemaids[lookup] = 'itemid="https://www.martineve.com/' + creator['name']['given'] + \
                            creator['name']['family'] + '"'
        schemaid = schemaids[lookup]
        shouldcreate = True

    if shouldcreate:
        creators += str.format(
            '<span itemtype="http://schema.org/Person" itemscope {2} itempropreplace><span itemprop="name"><span itemprop="familyName">{0}</span>, <span itemprop="givenName">{1}</span></span></span>',
            creator['name']['family'], creator['name']['given'], schemaid)
    else:
        creators += str.format(
            '<span itemtype="http://schema.org/Person" itemscope {2} itempropreplace>{0}, {1}</span>',
            creator['name']['family'], creator['name']['given'], schemaid)

    if 'editors' in item:
        for editor in item['editors'][:-1]:
            if editors == "":
                editors = ", ed. by "
            if editors != ", ed. by ":
                editors += ", "

            editors += str.format('{0}, {1}', editor['name']['family'],
                                  editor['name']['given'])

        if editors == "":
            editors = ", ed. by "
        if editors != ", ed. by ":
            editors += ", and "

        editor = item['editors'][-1]

        editors += str.format('{0}, {1}', editor['name']['family'],
                              editor['name']['given'])

    try:
        the_date = datetime.strptime(item['date'][0:4], "%Y").year
    except:
        the_date = "n.d."

    oa_status = ""
    if 'oa_status' in item:
        if item['oa_status'] == 'green' or item['oa_status'] == 'gold':
            oa_color = 'goldenrod' if item['oa_status'] == 'gold' else item['oa_status']
            if 'files' in item:
                oa_status = "[<a href=\"" + item['files'][0]['url'] + "\" style=\"color:" + oa_color + "\">Download</a>]"
            elif 'documents' in item:
                if len(item['documents']) > 1:
                    for doc in item['documents']:
                        if 'formatdesc' in doc:
                            oa_status += " [<a href=\"" + doc['uri'] + "\" style=\"color:" + oa_color + "\">Download " + doc['formatdesc'] + "</a>]"
                        else:
                            oa_status += " [<a href=\"" + doc['uri'] + "\" style=\"color:" + oa_color + "\">Download</a>]"
                else:
                    oa_status = "[<a href=\"" + item['documents'][0]['uri'] + "\" style=\"color:" + oa_color + "\">Download</a>]"
            else:
                oa_status = "[<a href=\"mailto:martin.eve@bbk.ac.uk?subject=Request to read '" + item['title'] + "'\">Email me to read</a>]"
    else:
        oa_status = "[<a href=\"mailto:martin.eve@bbk.ac.uk?subject=Request to read'" + item['title'] + "'\">Email me to read</a>]"

    if 'oa_status' in item and item['oa_status'] == 'gold' and 'official_url' in item:
        item['uri'] = item['official_url']

    # replace double quotation marks with singles
    item['title'] = item['title'].replace('"', '\'')
    item['title'] = item['title'].replace('“', '‘')
    item['title'] = item['title'].replace('”', '’')

    if item['type'] == 'book':
        if 'mailto:' in oa_status:
            oa_status = ""

        if item['ispublished'] == 'inpress':
            in_press = '[in press]'
        else:
            in_press = ''

        print('<li>{0}, <a href="{4}"><i>{1}</i></a>{5} ({2}: {3}) {6} {7}</li>'.format(creators,
                                                                                        item['title'],
                                                                                        item['publisher'],
                                                                                        the_date,
                                                                                        item['uri'],
                                                                                        editors,
                                                                                        oa_status,
                                                                                        in_press))

    if item['type'] == "article":
        creators_replaced = creators.replace('itempropreplace', 'itemprop="author"')
        # build the volume/number format
        volume = ""

        if 'volume' in item and not 'number' in item:
            volume = ' ({0})'.format(str(item['volume']))
        elif 'number' in item and not 'volume' in item:
            volume = ' {0}'.format(str(item['number']))
        elif 'number' in item and 'volume' in item:
            volume = ' {0}({1})'.format(str(item['volume']), str(item['number']))

        if item['ispublished'] == 'inpress':
            in_press = '[in press]'
        else:
            in_press = ''

        print ('<li><span itemscope itemtype="http://schema.org/CreativeWork" itemid="{5}">{0}, &ldquo;<a href="{5}"><span itemprop="name">{1}</span></a>&rdquo;, <i><span itemscope itemtype="http://schema.org/Periodical"><span id="name">{2}</span></span></i>{3}, <span itemprop="datepublished">{4}</span></span> {6} {7}</li>'.format(
            creators_replaced,
            item['title'],
            item['publication'],
            volume,
            the_date,
            item['uri'],
            oa_status,
            in_press))

    if item['type'] == "book_section":

        if item['ispublished'] == 'inpress':
            in_press = '[in press]'
        else:
            in_press = ''

        print ('<li>{0}, &ldquo;<a href="{6}">{1}</a>&rdquo;, in <i>{2}</i>{3} ({4}: {5}) {7} {8}</li>'.format(creators,
                                                                                                               item['title'],
                                                                                                               item['book_title'],
                                                                                                               editors,
                                                                                                               item['publisher'],
                                                                                                               the_date,
                                                                                                               item['uri'],
                                                                                                               oa_status,
                                                                                                               in_press))

    if item['type'] == "conference_item":
        creators_replaced = creators.replace('itempropreplace', 'itemprop="performer"')
        print (
            '<li><span itemscope itemtype="http://schema.org/EducationEvent" itemid="{5}">{0}, &ldquo;<a href="{5}">{1}</a>&rdquo;, <i><span itemprop="name">{2}</span></i>, <span itemscope itemtype="http://schema.org/Place" itemprop="location"><span itemprop="address"><span itemprop="name">{4}</span></span></span>, <span itemprop="startDate">{3}</span></span></li>'.format(
                creators_replaced,
                item['title'],
                item['event_title'],
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
    response = urlopen(url)
    json_data = response.read().decode('utf-8')

    # decode the JSON object into a list of dictionaries
    # NB that, helpfully, this list is by default reverse sorted (newest first)
    # should this ever change, it would need a lamda sort:
    # jsonSorted = sorted(list_to_be_sorted, key=lambda k: k['date'])
    json_list = json.loads(json_data)

    if args['--dump']:
        print(json_list)
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
                elif needs_ref != "ANY" and 'refereed' in currentItem and currentItem['refereed'] == needs_ref:
                    # this is an item of that type
                    do_print = True
                else:
                    do_print = False

                if do_print:
                    if rev == "ANY":
                        do_print = True
                    elif rev == "TRUE" and currentItem['title'].startswith("Review of"):
                        do_print = True
                    elif rev == "FALSE" and currentItem['title'].startswith("Review of") == False:
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
