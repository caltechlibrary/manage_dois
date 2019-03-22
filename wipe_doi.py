import os,json
from datacite import DataCiteMDSClient, schema40

def update_doi(doi,metadata,url=''):

    password = os.environ['DATACITE']
    prefix = doi.split('/')[0]
    #Ensure metadata identifier matches that given in function
    metadata['identifier'] = {'identifier':doi,'identifierType':'DOI'}

    # Initialize the MDS client.
    d = DataCiteMDSClient(
        username='TIND.CALTECH',
        password=password,
        prefix=prefix,
        url='https://mds.datacite.org'
        #test_mode=True
        )

    result =  schema40.validate(metadata)
    #Debugging if this fails
    if result == False:
        v = schema40.validator.validate(metadata)
        errors = sorted(v.iter_errors(instance), key=lambda e: e.path)
        for error in errors:
            print(error.message)
        exit()

    xml = schema40.tostring(metadata)

    response = d.metadata_post(xml)
    print(response)
    if url != '':
        response = d.doi_post(doi,url)
        print(response)

if __name__ == "__main__":
    with open('blank.json') as f:
        metadata = json.load(f)
    dois = [line.rstrip('\n') for line in open('dois.txt')]
    for doi in dois:        
        print(doi)
        update_doi(doi,metadata)#,'https://library.caltech.edu/dois')
