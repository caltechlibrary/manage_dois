import dataset
import requests
from caltechdata_api import get_metadata
from datacite import DataCiteMDSClient, schema40
import subprocess, os, datetime, sys

# Input CaltechDATA ID, Reource URL

idv = sys.argv[1]
url = sys.argv[2]

token = os.environ['TINDTOK']

prefix = '10.7907'

metadata = get_metadata(idv)
identifier = {"relatedIdentifier":url,
        'relatedIdentifierType':'URL','relationType':'IsDerivedFrom'}
if 'relatedIdentifers' in metadata:
    metadata['relatedIdentifiers'].append(identifier)
else:
    metadata['relatedIdentifiers']=[identifier]
                    
metadata['publisher'] = 'Caltech Library'        
        
metadata['resourceType'] = {"resourceTypeGeneral":'Other',
                    'resourceType':'Website'}        

#Get our DataCite password
infile = open('data/pw','r')
password = infile.readline().strip()

# Initialize the MDS client.
d = DataCiteMDSClient(
username='CALTECH.LIBRARY',
password=password,
prefix=prefix,
#test_mode=True
)

doi_end =subprocess.check_output(['./gen-cool-doi'],universal_newlines=True)
identifier = str(prefix)+'/'+str(doi_end)

metadata['identifier'] = {'identifier':identifier,'identifierType':'DOI'}

assert schema40.validate(metadata)
#Debugging if this fails
#v = schema40.validator.validate(metadata)
#errors = sorted(v.iter_errors(instance), key=lambda e: e.path)
#for error in errors:
#    print(error.message)

xml = schema40.tostring(metadata)
d.metadata_post(xml)
d.doi_post(identifier,url)
print('DOI minted:'+identifier)

metadata = {}

metadata['relatedIdentifiers'] =[{"relatedIdentifier":url,
                    'relatedIdentifierType':'URL','relationType':'IsSourceOf'}]

caltechdata_edit(token,idv,metadata)
