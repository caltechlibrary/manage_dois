import os,csv
from caltechdata_api import get_metadata
from datacite import DataCiteMDSClient, schema40

def update_doi_url(doi,url):

    password = os.environ['DATACITE']
    prefix = doi.split('/')[0]

    # Initialize the MDS client.
    d = DataCiteMDSClient(
        username='TIND.CALTECH',
        password=password,
        prefix=prefix,
        url='https://mds.datacite.org'
        )

    response = d.doi_post(doi,url)
    print(response)

if __name__ == "__main__":
    with open('dois.csv') as f:
        reader = csv.reader(f)
        urls = dict((rows[0],rows[1]) for rows in reader)
    for doi in urls:
        update_doi_url(doi,urls[doi])

