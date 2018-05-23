import dataset
from datacite import schema40
import os, datetime

new=True

now = datetime.datetime.now()

collection = 'website_requests.ds'
if os.path.isdir('data') == False:
    os.mkdir('data')
os.chdir('data')

if new==True:
    os.system('rm -rf '+collection)

if os.path.isdir(collection) == False:
    ok = dataset.init(collection)
    if ok == False:
        print("Dataset failed to init collection")
        exit()

client_secret = '/etc/client_secret.json'
sheet_id = '1A4XTcfcq5usHw-hKHoWTADwMAJAWM7sdha93wvLs6rM'
sheet_name = 'Form Responses 1'
cell_range = 'A1:Z'

archive_path = 'https://wayback.archive-it.org/9060/'

err= dataset.import_gsheet(collection,client_secret,sheet_id,
        sheet_name,cell_range,id_col=1, overwrite=True)

for key in dataset.keys(collection):
    inputv,err = dataset.read(collection,key)
    if err != "":
        t.error(f"Unexpected error for {key} in {collection_name}, {err}")
    #If we haven't assigned a doi for this resource before
    if inputv['doi'] == '':
        #Confirm that archiving is successful
        if inputv['complete'] == 'Yes':
            metadata = {}
            metadata['titles'] = [{'title':inputv['name']}]
            authors = []
            alist = inputv['author'].split(';')
            aff_list = inputv['affiliation'].split(';')
            orcid_list = inputv['orcid'].split(';')
            for aindex in range(len(alist)):
                author = {}
                author['creatorName'] = alist[aindex]
                if len(aff_list) > aindex:
                    author['affiliations'] = [aff_list[aindex]]
                if len(orcid_list) > aindex:
                    author['nameIdentifiers'] = [{'nameIdentifier':
                        orcid_list[aindex],'nameIdentifierScheme':'ORCID'}]
                authors.append(author)
            metadata['creators'] = authors
            if inputv['license'] != '':
                metadata['rightsList'] = [{'rights':inputv['license']}]
            metadata['relatedIdentifiers']=[{"relatedIdentifier":inputv['url'],
                    'relatedIdentifierType':'URL','relationType':'IsIdenticalTo'},
                    {"relatedIdentifier":archive_path+inputv['url'],
                    'relatedIdentifierType':'URL','relationType':'IsSourceOf'}]
            metadata['resourceType'] = {"resourceTypeGeneral":'Other',
                    'resourceType':'Website'}
            metadata['publicationYear'] = str(now.year)
            metadata['publisher'] = 'Caltech Library'
        else:
            print("Web archiving is not complete for "+inputv['title'])
    
    metadata['identifier'] = {'identifier':'10.1/1','identifierType':'DOI'}

    assert schema40.validate(metadata)
    #Debugging if this fails
    #v = schema40.validator.validate(metadata)
    #errors = sorted(v.iter_errors(instance), key=lambda e: e.path)
    #for error in errors:
    #    print(error.message)

    xml = schema40.tostring(metadata)

