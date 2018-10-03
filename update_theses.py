import requests, sys, csv

def update_record():
    print('hello')

def validate_response(response):
    if (response.status_code != 200):
        print(str(response.status_code) + " " + response.text)
        exit()
    else:
        return response.json()

endpoint = 'https://api.datacite.org/works'
query = endpoint + '?query=10.7907&data-center-id=caltech.library'
response = requests.get(query)
response = validate_response(response)
pages = response['meta']['total-pages']
records = response['data']

output = open('records.tsv','w')
writer = csv.writer(output, delimiter='\t')
writer.writerow(\
        ['Eprints ID','DOI','Degree Date','Author Name','Title','PURL'])
page = 1
count = 0
while page <= pages:
    for r in records:
        if r['attributes']['resource-type-subtype'] != 'Dissertation':
            author = r['attributes']['author'][0]
            if 'family' in author:
                name = author['family']+', '+author['given']
            elif 'literal' in author:
                name = author['literal']
            else:
                print(r['attributes']['author'][0])
                exit()
            print(r['attributes']['doi'])
            writer.writerow(['',r['attributes']['doi'],\
            r['attributes']['published'],name,r['attributes']['title'],\
            r['attributes']['url']])
        count = count + 1
    page = page + 1
    response = requests.get(query + '&page[number]='+str(page))
    response = validate_response(response)
    records = response['data']
print(count)
