from py_dataset import dataset
import requests
from datacite import DataCiteMDSClient, schema40
import subprocess, os, datetime

def send_simple_message(token,email,doi,url):
    return requests.post(
        "https://api.mailgun.net/v3/notices.caltechlibrary.org/messages",
        auth=("api", token),
        files=[("inline", open("CaltechLibraryLogo.gif",'rb'))],
        data={"from": "Caltech Library Notices <mail@notices.caltechlibrary.org>",
              "to": email+" <"+email+">",
              "subject": "Your Requested Website DOI is Available",
              "html": '<html> <center> <img src="cid:CaltechLibraryLogo.gif"\
                      alt="Caltech Library Logo"> </center> \
                      <p> Hello, </p>\
                      <p>You requested a DOI for the web site "'+url+'".\
                      This web site has been successfuly archived and a DOI\
                      has been generated: \
                      <a href="https://doi.org/'+doi+'">'+doi+'</a>.</p>\
                      <p> Best, </p><p>Caltech Library</p><hr>\
                      <p> See an issue?  Let us know at\
                      <a href="mailto:library@caltech.edu?Subject=Issue%20with%20web%20archive%20'\
                      +doi+'">library@caltech.edu</a></p>\
                      <P> This email was sent by the Caltech Library, \
                      1200 East California Blvd., MC 1-43, Pasadena, CA 91125, USA </p> </html>'})

new=False

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
cell_range = 'A2:Z'

archive_path = 'https://wayback.archive-it.org/9060/'

err = dataset.import_gsheet(collection,sheet_id,
        sheet_name,1,cell_range,overwrite=True)
if err != '':
    print(f"Unexpected error on importing gsheet to {collection}, {err}")
    exit()

keys = dataset.keys(collection)

for key in keys:
    inputv,err = dataset.read(collection,key)
    if err != "":
        print(f"Unexpected error for {key} in {collection}, {err}")
        exit()
    #If we haven't assigned a doi for this resource before
    if 'doi' not in inputv:
        #Confirm that archiving is successful
        if 'archive_complete' in inputv:
            if inputv['archive_complete'] == 'Yes':
                metadata = {}
                metadata['titles'] = [{'title':inputv['title']}]
                authors = []
                alist = inputv['author'].split(';')
                if 'affiliation' in inputv:
                    aff_list = inputv['affiliation'].split(';')
                else:
                    aff_list = []
                if 'orcid' in inputv:
                    orcid_list = inputv['orcid'].split(';')
                else:
                    orcid = []
                for aindex in range(len(alist)):
                    author = {}
                    author['creatorName'] = alist[aindex].strip()
                    if len(aff_list) > aindex:
                        author['affiliations'] = [aff_list[aindex].strip()]
                    if len(orcid_list) > aindex:
                        author['nameIdentifiers'] = [{'nameIdentifier':
                        orcid_list[aindex].strip(),'nameIdentifierScheme':'ORCID'}]
                    authors.append(author)
            metadata['creators'] = authors
            if 'license' in inputv:
                metadata['rightsList'] = [{'rights':inputv['license']}]
            metadata['relatedIdentifiers']=[{"relatedIdentifier":inputv['url'],
                    'relatedIdentifierType':'URL','relationType':'IsIdenticalTo'},
                    {"relatedIdentifier":archive_path+inputv['url'],
                    'relatedIdentifierType':'URL','relationType':'IsSourceOf'}]
            metadata['resourceType'] = {"resourceTypeGeneral":'Other',
                    'resourceType':'Website'}
            metadata['publicationYear'] = str(now.year)
            metadata['publisher'] = 'Caltech Library'

            #Get the prefix to use
            prefix = inputv['prefix'].split('(')[1].split(')')[0]
            #prefix = '10.5072'

            #Get our DataCite password
            infile = open('pw','r')
            password = infile.readline().strip()

            # Initialize the MDS client.
            d = DataCiteMDSClient(
            username='CALTECH.LIBRARY',
            password=password,
            prefix=prefix,
            )

            identifier = str(prefix)

            metadata['identifier'] = {'identifier':identifier,'identifierType':'DOI'}

            #assert schema40.validate(metadata)
            #Debugging if this fails
            #v = schema40.validator.validate(metadata)
            #errors = sorted(v.iter_errors(instance), key=lambda e: e.path)
            #for error in errors:
            #    print(error.message)
            xml = schema40.tostring(metadata)
            result = d.metadata_post(xml)
            identifier = result.split('(')[1].split(')')[0]
            d.doi_post(identifier,inputv['url'])
            print('Completed '+identifier)

            inputv['doi'] = identifier
            err = dataset.update(collection,key,inputv)

            token = os.environ['MAILTOK']

            email = inputv['email']
            url = inputv['url']

            send_simple_message(token,email,identifier,url)

        else:
            print("Web archiving is not complete for "+inputv['name'])

dot_exprs =\
['.email','.url','.title','.author','.affiliation','.orcid','.license','.prefix','.archive_complete','.doi']
column_names = ['email','url','title','author','affiliation','orcid','license','prefix','archive_complete','doi']
frame_name = 'export'

if dataset.has_frame(collection, frame_name):
    dataset.delete_frame(collection, frame_name)
(f1, err) = dataset.frame(collection, frame_name, keys, dot_exprs, column_names)

err =  dataset.sync_send_gsheet(collection, frame_name, sheet_id, sheet_name,
        cell_range, overwrite = False)
if err != '':
    print("Failed, count not export-gsheet in", collection_name, ', ', err)
