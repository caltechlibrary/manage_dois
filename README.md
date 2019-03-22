# manage_dois

Scripts to manage custom DOIs

Requires: 

Python 3 (Recommended via [Anaconda](https://www.anaconda.com/download)) with [requests](https://pypi.python.org/pypi/requests) library and [Dataset](https://github.com/caltechlibrary/dataset).

Set your DataCite password by making a file 'pw' under the directory 'data'

## DOIs for Web Sites

- web_doi.py - Search google sheet for archived web sites that need DOIs
- static_content.py - Takes a CaltechDATA id and url for the web view of an
  interactive resource stored in CaltechDATA  

## TCCON New Site Release

- Get a .xlsx metadata template (TCCON_Metadata_Template.xlsx) completed by the site PI.
  Type `python tccon_doi.py template.xlsx` to generate a .json metadata file.
  Transfer to TCCON server. Make sure the site has a web site (e.g.
  https://tccon-wiki.caltech.edu/Sites/Hefei) and add to
  create_readme_contents_tccon-data. Type ./run_new_site hf 

