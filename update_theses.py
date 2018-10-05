import requests, sys, csv, getpass,subprocess
import xmltodict
import caltech_thesis
from datacite import schema40,DataCiteMDSClient

def update_record(idv,username,password,datacite_password):
    url = 'https://'+username+':'+password+'@thesis.library.caltech.edu/rest/eprint/'
    record_url = url + str(idv) +'.xml'
    record = subprocess.check_output(["eputil",record_url],universal_newlines=True)
    eprint = xmltodict.parse(record)['eprints']['eprint'] 
    metadata = caltech_thesis.epxml_to_datacite(eprint)
    
    assert schema40.validate(metadata)
    #Debugging if this fails
    #v = schema40.validator.validate(metadata)
    #errors = sorted(v.iter_errors(instance), key=lambda e: e.path)
    #for error in errors:
    #        print(error.message)

    # Initialize the MDS client.
    d = DataCiteMDSClient(
    username='CALTECH.LIBRARY',
    password=datacite_password,
    prefix='10.7907',
    )

    xml = schema40.tostring(metadata)
    result = d.metadata_post(xml)
    print(result)

def validate_response(response):
    if (response.status_code != 200):
        print(str(response.status_code) + " " + response.text)
        exit()
    else:
        return response.json()

def trace_url(url):
    get = requests.get(url)
    return get.url

username = input('Enter your username: ')
password = getpass.getpass()

#Get our DataCite password
infile = open('pw','r')
datacite_password = infile.readline().strip()

endpoint = 'https://api.datacite.org/works'
query = endpoint + '?query=10.7907&data-center-id=caltech.library'
response = requests.get(query)
response = validate_response(response)
pages = response['meta']['total-pages']
records = response['data']

output = open('records.tsv','w')
writer = csv.writer(output, delimiter='\t')
writer.writerow(\
        ['Eprints ID','DOI','Degree Date','Author Name','Title','URL'])
page = 1
count = 0
while page <= pages:
    for r in records:
        author = r['attributes']['author'][0]
        if 'family' in author:
            name = author['family']+', '+author['given']
        elif 'literal' in author:
            name = author['literal']
        else:
            print(r['attributes']['author'][0])
            exit()
        doi = r['attributes']['identifier']
        print(doi)
        url = trace_url(doi)
        split = url.split('/')
        if split[2]=='thesis.library.caltech.edu':
                update_record(split[3],username,password,datacite_password)
                writer.writerow(['',r['attributes']['doi'],\
                r['attributes']['published'],name,r['attributes']['title'],url])
        count = count + 1
    page = page + 1
    response = requests.get(query + '&page[number]='+str(page))
    response = validate_response(response)
    records = response['data']
print(count)
