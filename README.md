eprintsCV
=========

A script to generate a list of academic publications in a web/CV-friendly format for academic websites.

Ascertain your eprints id and your repository url and then use:

./eprintsCV.py URL ID "book,article,book_section,conference_item"

So, for example:

./eprintsCV.py eprints.lincoln.ac.uk 3354 "book,article,book_section,conference_item"

On an eprints3 server with named identifiers, as opposed to numeric identifiers, you should use something like:

./eprintsCV_eprints3.py eprints.bbk.ac.uk Eve=3AMartin_Paul=3A=3A "book,article,book_section,conference_item"
