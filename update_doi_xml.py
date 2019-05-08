import os,json
from datacite import DataCiteMDSClient, schema40

def update_doi(doi,xml,url=''):

    password = os.environ['DATACITE']
    prefix = doi.split('/')[0]

    # Initialize the MDS client.
    d = DataCiteMDSClient(
        username='CALTECH.LIBRARY',
        password=password,
        prefix=prefix,
        url='https://mds.datacite.org'
        #test_mode=True
        )

    response = d.metadata_post(xml)
    print(response)
    if url != '':
        response = d.doi_post(doi,url)
        print(response)

if __name__ == "__main__":
    with open('92929_datacite.xml') as f:
        metadata = f.read()
    doi = '10.26206/m04t-y423'
    update_doi(doi,metadata)

