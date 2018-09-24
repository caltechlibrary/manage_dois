# Take data from a spreadsheet and turn it into DataCite metadata
# Requires xlsx2json[https://github.com/caltechlibrary/datatools]

import os,argparse

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

for s in sheets:
    os.system('xlsx2json ../'+args.xlsx_file[0]+" "+s+" > "+s+".json")




