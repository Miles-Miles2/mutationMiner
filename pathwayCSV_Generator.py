import sys

sys.path.append('../')

import logging
import csv
import traceback as tb
import suds.metrics as metrics
from suds import *
from suds.client import Client
from datetime import datetime


import xlsxwriter

logging.getLogger('suds.client').setLevel(logging.DEBUG)

url = 'https://david.ncifcrf.gov/webservice/services/DAVIDWebService?wsdl'

client = Client(url)
client.wsdl.services[0].setlocation(
    'https://david.ncifcrf.gov/webservice/services/DAVIDWebService.DAVIDWebServiceHttpSoap11Endpoint/')

client.service.authenticate('mkeiser@curescience.org')

conversions = {}

with open("CellLineNameToCCLE_ID.csv") as converterCSV:
    dictReader = csv.DictReader(converterCSV)
    for row in dictReader:
        conversions[row['DepMap_ID']] = row['stripped_cell_line_name']


cellLine = ""

mutationsDict = {}


with open("mutationsCSV.csv") as sourceCSV:
    csvDict = csv.DictReader(sourceCSV)
    for row in csvDict:

        name = row['cellLineName']#conversions[row['cellLineName']]
        mutationsDict[name] = []
        for item in row.items():
            if item[1] == 'mutation':
                mutationsDict[name].append(item[0])


gene_symbol_to_entrez = {}

with open("GENE_SYMBOL_to_ENTREZ_ID_CSV.csv") as converterCSV:
    dict = csv.DictReader(converterCSV)
    for row in dict:
        gene_symbol_to_entrez[row['gene_symbol']] = row['entrez']




mainList = {}




counter = 0

for cellLine, mutationList in mutationsDict.items():
    davidInput = []
    for mutatedGene in mutationList:
        if mutatedGene in gene_symbol_to_entrez.keys():
            davidInput.append(gene_symbol_to_entrez[mutatedGene])

    print("Submitting " + str(len(davidInput)) + " genes to DAVID for " + cellLine)

    inputIds = ','.join(davidInput)
    idType = "ENTREZ_GENE_ID"
    listName = cellLine
    listType = 0

    client.service.addList(inputIds, idType, listName, listType)
    allLists = str(client.service.getAllListNames()).split(',')

    client.service.setCurrentList(len(allLists)-1)
    client.service.setCategories("KEGG_PATHWAY")

    summary = client.service.getChartReport(999, 0)

    counter = 0
    mainList[cellLine] = []
    for record in summary:
        mainList[cellLine].append(record.termName.replace(",","-"))
        counter += 1
    print("# pathways added:" + str(counter))

print("******************************************")


#mainList = {'ACH-000201': [1, 2, 3], 'ACH-000228': [1, 3, 9, 0]}

totalPathways = []

print("Generating list of all pathways **************************")
for mutationList in mainList.values():
    print("PATHWAYS:")
    for pathway in mutationList:
        if pathway not in totalPathways:
            totalPathways.append(pathway)
            
totalPathways.append('class')

outputDict = {}

print("Generating Empty Dict")
for cellLine in mainList.keys():
    outputDict[cellLine] = {}
    for pathway in totalPathways:
        if not (pathway == 'class'):
            outputDict[cellLine][pathway] = "notMutated"


print("Setting mutated pathways to 'mutated' in output dict")
for cellLine in outputDict.keys():
    for mutatedPathway in mainList[cellLine]:
        outputDict[cellLine][mutatedPathway] = 'mutation'


#ADD RADIOSENSITIVITY
mutationsAndRadiosensitivityDict = {}

with open("CCLE_mutations_with_radiosensitivity.csv") as mutationsAndRadiosensitivity:
    csvDict = csv.DictReader(mutationsAndRadiosensitivity)
    for row in csvDict:
        mutationsAndRadiosensitivityDict[row['cellLineName']] = row


for cellLine, mutationDict in outputDict.items():
    outputDict[cellLine]['class'] = mutationsAndRadiosensitivityDict[cellLine]['radiosensitivity']

#ADD CELL LINE NAME

totalPathways.append('cellLineName')
for cellLineName in outputDict:
    outputDict[cellLineName]['cellLineName'] = cellLineName


with open(
    'pathwayFINAL_OUTPUT.csv',
    'w',
    newline=''
) as outputCSV:
    fieldnames = totalPathways
    csvDictWriter = csv.DictWriter(outputCSV, fieldnames=fieldnames)
    csvDictWriter.writeheader()

    for cellLine in outputDict:
        csvDictWriter.writerow(outputDict[cellLine])

'''
workbook = xlsxwriter.Workbook('singleCellLinePathways.xlsx')
worksheet = workbook.add_worksheet()

count = 0

worksheet.write(0,0, "All Genes")
worksheet.write(0,1, "All Pathways")
worksheet.write(0,2, "P-Value")
worksheet.write(0, 3, "Cell Line: " + cellLine)
for i in range(0, len(davidInput)):
    worksheet.write(i+1, 0, davidInput[i])

for i in range(len(davidOutputOfPathways)):
    worksheet.write(i+1, 1, davidOutputOfPathways[i][0])
    worksheet.write(i + 1, 2, davidOutputOfPathways[i][1])

workbook.close()


#TODO: GET P VALUE
'''
