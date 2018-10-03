import requests, sys

endpoint = 'https://api.datacite.org/works'
response = requests.get(endpoint +\
        '?query=10.7907&data-center-id=caltech.library')

if (response.status_code != 200):
    print(str(response.status_code) + " " + response.text)
    exit()
else:
    records = response.json()['data']

for r in records:
    print(r['attributes']['resource-type-subtype'])
