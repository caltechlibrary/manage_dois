import os,json
from datacite import DataCiteMDSClient, schema40


def create_doi(metadata,url):

    password = os.environ['DATACITE']
    prefix = '10.33569'

    # Initialize the MDS client.
    d = DataCiteMDSClient(
            username='CALTECH.LIBRARY',
            password=password,
            prefix=prefix,
            url='https://mds.test.datacite.org'
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

    #Provide only prefix in identifier field to let DataCite generate DOI
    metadata['identifier'] = {'identifier':prefix,'identifierType':'DOI'}

    xml = schema40.tostring(metadata)

    response = d.metadata_post(xml)
    print(response)
    identifier = response.split('(')[1].split(')')[0]
    response = d.doi_post(identifier,url)
    print(response)

if __name__ == "__main__":
    with open('example.json') as f:
        metadata = json.load(f)
    create_doi(metadata,'https://library.caltech.edu')
