import os,json,getpass,csv
import requests,xmltodict
from caltech_authors_tech_report import epxml_to_datacite
from datacite import DataCiteMDSClient, schema40
from epxml_support import download_records

def update_doi(doi,metadata,url=''):

    password = os.environ['DATACITE']
    prefix = doi.split('/')[0]
    #Ensure metadata identifier matches that given in function
    metadata['identifier'] = {'identifier':doi,'identifierType':'DOI'}

    # Initialize the MDS client.
    d = DataCiteMDSClient(
        username='CALTECH.LIBRARY',
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

    r_user = input('Enter your CaltechAUTHORS username: ')
    r_pass = getpass.getpass()

    with open('keck_tech_reports.csv') as infile:
        reader = csv.reader(infile, delimiter=',')
        for row in reader:
            if row[0] != 'Eprint ID':
                download_records([row[0]],'authors',r_user,r_pass)
                with open(row[0]+'.xml',encoding="utf8") as fd:
                    eprint = xmltodict.parse(fd.read())['eprints']['eprint']
                metadata = epxml_to_datacite(eprint,'KISS')
                update_doi(row[1],metadata)
