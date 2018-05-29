# manage_dois

Scripts to manage custom DOIs

Requires: 

Python 3 (Recommended via [Anaconda](https://www.anaconda.com/download)) with [requests](https://pypi.python.org/pypi/requests) library and [Dataset](https://github.com/caltechlibrary/dataset).

base32-url from DataCite.  You can install this ruby gem on a modern Mac by
typing 'sudo gem install -n /usr/local/bin base32-url'

Set your DataCite password by making a file 'pw' under the directory 'data'

## DOIs for Web Sites

- web_doi.py - Search google sheet for archived web sites that need DOIs
- static_content.py - Takes a CaltechDATA id and url for the web view of an
  interactive resource stored in CaltechDATA  

