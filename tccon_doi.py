# Take data from a spreadsheet and turn it into DataCite metadata
# Requires xlsx2json[https://github.com/caltechlibrary/datatools]

import os,argparse,json,datetime
from datacite import schema40

parser = argparse.ArgumentParser(description=\
        "Take info from a spreadsheet and turn it into DataCite metadata")
parser.add_argument('xlsx_file', nargs=1, help=\
            'file name for xlsl file with TCCON metadata')
args = parser.parse_args()

if os.path.isdir('data') == False:
    os.mkdir('data')
os.chdir('data')

sheets=['site','creators','contributors','related_identifier',\
        'funding_references']

files = {}

for s in sheets:
    os.system('xlsx2json ../'+args.xlsx_file[0]+" "+s+" > "+s+".json")
    infile = open(s+".json",'r')
    files[s] = json.load(infile)

#print(files['site'])
#print(files['creators'])

metadata = {}

site_info = files['site'][1]

alternate_identifiers =\
[{"alternateIdentifier":"GGG2014","alternateIdentifierType":"Software_Version"},{"alternateIdentifier":"R0","alternateIdentifierType":"Data_Revision"}]
alternate_identifiers.append({"alternateIdentifier":site_info[2],"alternateIdentifierType":"id"})
alternate_identifiers.append({"alternateIdentifier":site_info[1],"alternateIdentifierType":"longName"})

metadata['alternateIdentifiers'] = alternate_identifiers

contributors = [{
            "affiliations": [
                "California Institute of Technology, Pasadena, CA (US)"
            ],
            "contributorName": "Roehl, C. M.",
            "contributorType": "DataCurator",
            "familyName": "Roehl",
            "givenName": "Coleen M.",
            "nameIdentifiers": [
                {
                    "nameIdentifier": "0000-0001-5383-8462",
                    "nameIdentifierScheme": "ORCID",
                    "schemeURI": "http://orcid.org/"
                }
            ]
        }]

line_n = 1
line = files['contributors'][line_n]
while line[0] != '':
    contributor = {}
    contributor['contributorType'] = line[0]
    contributor['familyName'] = line[1]
    contributor['givenName'] = line[2]
    contributor['contributorName'] = line[1]+', '+line[2]
    if line[3] != '':
        contributor['affiliations'] = [line[3]]
    if line[4] != '':
        contributor['nameIdentifiers'] = [{
        'nameIdentifier':line[4],'nameIdentifierScheme':'ORCID','schemeURI':'https://orcid.org'}]
    if line[5] != '':
        identifier =\
        {'nameIdentifier':line[5],'nameIdentifierScheme':'ResearcherID','schemeURI':'http://www.researcherid.com/rid/'}
        if 'nameIdentifiers' in contributor:
            contributor['nameIdentifiers'].append(identifier)
        else:
            contributor['nameIdentifiers'] = [identifier]
    contributors.append(contributor)
    line_n = line_n + 1
    line = files['contributors'][line_n]

metadata['contributors'] = contributors

creators = []
line_n = 1
line = files['creators'][line_n]
while len(line) > 1:
    creator = {}
    creator['familyName'] = line[0]
    creator['givenName'] = line[1]
    creator['creatorName'] = line[0]+', '+line[1]
    if line[2] != '':
        creator['affiliations'] = [line[2]]
    if line[3] != '':
        creator['nameIdentifiers'] = [{
        'nameIdentifier':line[3],'nameIdentifierScheme':'ORCID','schemeURI':'https://orcid.org'}]
    if line[4] != '':
        identifier =\
        {'nameIdentifier':line[4],'nameIdentifierScheme':'ResearcherID','schemeURI':'http://www.researcherid.com/rid/'}
        if 'nameIdentifiers' in contributor:
            creator['nameIdentifiers'].append(identifier)
        else:
            creator['nameIdentifiers'] = [identifier]
    creators.append(creator)
    line_n = line_n + 1
    line = files['creators'][line_n]
metadata['creators'] = creators

description_text = "The Total Carbon Column Observing Network (TCCON) is a\
 network of ground-based Fourier Transform Spectrometers that record direct\
 solar absorption spectra of the atmosphere in the near-infrared. From these\
 spectra, accurate and precise column-averaged abundances of atmospheric\
 constituents including CO2, CH4, N2O, HF, CO, H2O, and HDO, are retrieved.\
 This data set contains observations from the TCCON station at "

metadata['descriptions'] = [{'description':description_text + \
        site_info[0]+'.','descriptionType':'Abstract'}]

metadata['formats'] = ['application/x-netcdf']

funding = []

line_n = 1
line = files['funding_references'][line_n]
while len(line) > 1:
    fund = {}
    fund['funderName'] = line[0]
    if line[1] != '':
        fund['funderIdentifier'] =\
        {'funderIdentifierType':line[1],'funderIdentifier':line[2]}
    if line[3] != '':
        if line[4] != '':
            fund['awardNumber']={'awardNumber':line[3],'awardURI':line[4]}
        else:
            fund['awardNumber']={'awardNumber':line[3]}
    if line[5] != '':
        fund['awardTitle'] = line[5]
    funding.append(fund)
    line_n = line_n + 1
    line = files['funding_references'][line_n]

metadata['fundingReferences'] = funding

metadata['geoLocations'] = [{'geoLocationPlace':site_info[3],\
        'geoLocationPoint':{'pointLatitude':float(site_info[4]),'pointLongitude':float(site_info[5])}}]

metadata['identifier'] =\
        {'identifier':'10.14291/tccon.ggg2014.'+site_info[1]+'.R0','identifierType':'DOI'}

metadata['language'] = 'en'
metadata['publicationYear'] = str(datetime.datetime.now().year)
metadata['publisher'] = 'CaltechDATA'

related = [{
            "relatedIdentifier": "https://tccondata.org/",
            "relatedIdentifierType": "URL",
            "relationType": "IsPartOf"
        },
        {
            "relatedIdentifier": "10.14291/tccon.ggg2014.documentation.R0/1221662",
            "relatedIdentifierType": "DOI",
            "relationType": "IsDocumentedBy"
        },
        {
            "relatedIdentifier": "https://tccon-wiki.caltech.edu/Network_Policy/Data_Use_Policy/Data_Description",
            "relatedIdentifierType": "URL",
            "relationType": "IsDocumentedBy"
        },
        {
            "relatedIdentifier": "https://tccon-wiki.caltech.edu/Sites",
            "relatedIdentifierType": "URL",
            "relationType": "IsDocumentedBy"
        },
        {
            "relatedIdentifier": "10.14291/TCCON.GGG2014",
            "relatedIdentifierType": "DOI",
            "relationType": "IsPartOf"
        }]

line_n = 1
line = files['related_identifier'][line_n]
while line[2] != '':
    rel = {}
    rel['relatedIdentifier'] = line[2]
    rel['relatedIdentifierType'] = line[1]
    rel['relationType'] = line[0]
    related.append(rel)
    line_n = line_n + 1
    line = files['related_identifier'][line_n]

metadata['relatedIdentifiers'] = related

metadata['resourceType'] = {'resourceTypeGeneral':'Dataset'}

metadata['subjects'] = [{'subject':"atmospheric trace gases"},{"subject":"CO2"},
    {"subject": "CH4"},{"subject": "CO"},{"subject": "N2O"},
    {"subject":"column-averaged dry-air mole fractions"},
    {"subject": "remote sensing"},{"subject": "FTIR spectroscopy"},
    {"subject": "TCCON"}]

metadata['titles'] = [{'title':"TCCON data from "+site_info[0]+\
        ", Release GGG2014.R0"}]

metadata['version'] = 'GGG2014.R0'

result =  schema40.validate(metadata)
#Debugging if this fails
if result == False:
    v = schema40.validator.validate(metadata)
    errors = sorted(v.iter_errors(instance), key=lambda e: e.path)
    for error in errors:
        print(error.message)
    exit()

json = json.dumps(metadata)
outfile = open('../'+site_info[1]+'.json','w')
outfile.write(json)
