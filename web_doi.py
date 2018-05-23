import dataset
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
                author['creatorName'] = alist[aindex].strip()
                if len(aff_list) > aindex:
                    author['affiliations'] = [aff_list[aindex].strip()]
                if len(orcid_list) > aindex:
                    author['nameIdentifiers'] = [{'nameIdentifier':
                        orcid_list[aindex].strip(),'nameIdentifierScheme':'ORCID'}]
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
            #test_mode=True
            )

            doi_end =subprocess.check_output(['../gen-cool-doi'],universal_newlines=True)
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
            d.doi_post(identifier,inputv['url'])
            print('Completed')

            token = os.environ['MAILTOK']

            email = inputv['email']
            url = inputv['url']

            send_simple_message(token,email,identifier,url)
            

        else:
            print("Web archiving is not complete for "+inputv['title'])
