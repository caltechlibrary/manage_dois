import requests, sys, csv, getpass,subprocess
import xmltodict
import caltech_authors_tech_report
from datacite import schema40,DataCiteMDSClient

def check_record(idv,username,password):
    url = 'https://'+username+':'+password+'@authors.library.caltech.edu/rest/eprint/'
    record_url = url + str(idv) +'.xml'
    record = subprocess.check_output(["eputil",record_url],universal_newlines=True)
    eprint = xmltodict.parse(record)['eprints']['eprint']

    name_and_series_exceptions = []
    if 'other_numbering_system' in eprint:
        if isinstance(eprint['other_numbering_system']['item'],list) == False:
            #Deal with single item listings
            eprint['other_numbering_system']['item'] = [eprint['other_numbering_system']['item']]

    if 'series_name' in eprint and 'number' in eprint:
        name_and_series = [eprint['series_name'],eprint['number']]
    elif 'other_numbering_system' in eprint:
        ids = []
        #Assume first is correct
        item = eprint['other_numbering_system']['item'][0]
        name_and_series_exceptions =\
        [item['name']['#text'],item['id'],'other_numbering',eprint['official_url']]
    elif 'local_group' in eprint:
        resolver = eprint['official_url'].split(':')
        number = resolver[-1]
        name_and_series_exceptions =\
            [eprint['local_group']['item'],number,'local_group_resolver',eprint['official_url']]
    else:
        resolver = eprint['official_url'].split(':')
        name = resolver[1].split('/')[-1]
        number = resolver[-1]
        name_and_series_exceptions =\
            [name,number,'resolver',eprint['official_url']]

    try:
        metadata = caltech_authors_tech_report.epxml_to_datacite(eprint)

    except:
        print ("Incorrect document type- skipping")
        pass
        return []

    try:
        assert schema40.validate(metadata)
    except:
        #Debugging if this fails
        v = schema40.validator.validate(metadata)
        errors = sorted(v.iter_errors(instance), key=lambda e: e.path)
        for error in errors:
            print(error.message)

    return name_and_series_exceptions

def update_record(idv,username,password,datacite_password):
    url = 'https://'+username+':'+password+'@authors.library.caltech.edu/rest/eprint/'
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

output = open('tech_report_exceptions.tsv','w')
writer = csv.writer(output, delimiter='\t')
#writer.writerow(\
        #        ['Eprints ID','DOI','Degree Date','Author Name','Title','URL'])
page = 1
count = 0
while page <= pages:
    for r in records:
        doi = r['attributes']['identifier']
        print(doi)
        author = r['attributes']['author'][0]
        if 'family' in author:
            name = author['family']+', '+author['given']
        elif 'literal' in author:
            name = author['literal']
        else:
            print(r['attributes']['author'][0])
            print("Check record in DataCite")
        url = trace_url(doi)
        split = url.split('/')
        if split[2]=='authors.library.caltech.edu':
            exceptions = check_record(split[3],username,password)
            #update_record(split[3],username,password,datacite_password)
            print(exceptions)
            print(len(exceptions))
            if len(exceptions) != 0:
                writer.writerow(exceptions)
        count = count + 1
    page = page + 1
    response = requests.get(query + '&page[number]='+str(page))
    response = validate_response(response)
    records = response['data']
print(count)
