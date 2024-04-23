import csv

#DAVID STUFF

import sys
sys.path.append('../')
import logging
from suds.client import Client

logging.getLogger('suds.client').setLevel(logging.DEBUG)
url = 'https://david.ncifcrf.gov/webservice/services/DAVIDWebService?wsdl'
client = Client(url)
client.wsdl.services[0].setlocation(
    'https://david.ncifcrf.gov/webservice/services/DAVIDWebService.DAVIDWebServiceHttpSoap11Endpoint/')
client.service.authenticate('mkeiser@curescience.org')


#actual DAVID code
mutationsDict = {}

gene_symbol_to_entrez = {}

with open("GENE_SYMBOL_to_ENTREZ_ID_CSV.csv") as converterCSV:
    dict = csv.DictReader(converterCSV)
    for row in dict:
        gene_symbol_to_entrez[row['gene_symbol']] = row['entrez']

def createPathwayList(mutationList):
    davidInput = []
    for mutatedGene in mutationList:
        if mutatedGene in gene_symbol_to_entrez.keys():
            davidInput.append(gene_symbol_to_entrez[mutatedGene])

    print("Submitting " + str(len(davidInput)) + " genes to DAVID")
    inputIds = ','.join(davidInput)
    idType = "ENTREZ_GENE_ID"
    listName = "noName"
    listType = 0

    client.service.addList(inputIds, idType, listName, listType)
    allLists = str(client.service.getAllListNames()).split(',')
    client.service.setCurrentList(len(allLists) - 1)
    client.service.setCategories("KEGG_PATHWAY")

    summary = client.service.getChartReport(999, 0)
    print(summary)
    outputPathwayList = []
    counter = 0
    for record in summary:
        outputPathwayList.append(record.termName)
        counter += 1
    print(str(counter) + " pathways added")
    return outputPathwayList

#---------------------------------------------------

outputDict = {}
fieldNames = []

#create list of mutations from from paper
line1 = []
line2 = []
line3 = []
line4 = []
line5 = []
line6 = []

with open("validationData/patientMutations.csv") as sourceCSV:
    csvDict = csv.DictReader(sourceCSV)

    for row in csvDict:
        if row["N1_site_type"] != ".":
            line1.append(row["NAME"])
        elif row["N2_site_type"] != ".":
            line2.append(row["NAME"])
        elif row["N3_site_type"] != ".":
            line3.append(row["NAME"])
        elif row["S1_site_type"] != ".":
            line4.append(row["NAME"])
        elif row["S2_site_type"] != ".":
            line5.append(row["NAME"])
        elif row["S3_site_type"] != ".":
            line6.append(row["NAME"])



with open('attributeSelected_2_noRSV.csv') as source:
    csvDict = csv.DictReader(source)

    for row in csvDict:
        fieldNames = list(row.keys())
        break

print(fieldNames)
print(len(fieldNames))

def addCellLine(name, mutationList, isRealCellLine, defaultValue="notMutated", radiosensitivityValue="radiosensitive"):
    outputDict[name] = {}
    mutationsFound = 0
    pathwaysFound = 0

    for attribute in fieldNames:
        outputDict[name][attribute] = defaultValue
    print("Adding following genes: ")
    for mutation in mutationList:
        if mutation in set(outputDict[name].keys()):
            print(mutation)
            outputDict[name][mutation] = "mutation"
            mutationsFound+=1
    if isRealCellLine == True:
        pathwayList = createPathwayList(mutationList)

        for pathway in pathwayList:
            if pathway in set(outputDict[name].keys()):
                outputDict[name][pathway] = "mutation"
                pathwaysFound += 1

    if (isRealCellLine == True):
        outputDict[name]['class'] = '?'
    else:
        outputDict[name]['class'] = radiosensitivityValue

    print(str(mutationsFound) + " mutations found | " + str(pathwaysFound) + " pathways found")



#addCellLine("patient1", ["MIS12", "OCRL", "ATAD1", "TRABD2A", "OR2T10", "PRDM9", "PCDHB5", "LPAR3", "MTUS2", "ZBTB48", "FAT3", "SCN9A", "SIM1", "CSRNP2", "OR4S1", "FGFR3", "DHCR24", "OR4C12", "AHNAK2", "CNGB1", "TMEM132D", "HMCN1", "DZIP1L", "DNAH14", "MECOM", "RRP12", "EGF", "SHF", "CAPNS1", "PCDHB8", "NAT10", "PDE8A", "ASPN", "EXPH5", "FMR1", "CD163L1", "EXOSC10", "TP53", "PTEN", "TERT"], [], True)
addCellLine("N1", line1, True, "notMutated")
addCellLine("N2", line2, True, "notMutated")
addCellLine("N3", line3, True, "notMutated")
addCellLine("S1", line4, True, "notMutated")
addCellLine("S2", line5, True, "notMutated")
addCellLine("S3", line6, True, "notMutated")

addCellLine("extra1", [], False, "notMutated", "radiosensitive")
addCellLine("extra2", [], False, "mutation", "normal")
addCellLine("extra3", [], False, "notMutated", "radioresistant")

for cellLine in outputDict:
    print(len(outputDict[cellLine].items()))


with open(
    "realWorldMutations.csv",
    "w",
    newline='') as outputCSV:
    csvDictWriter = csv.DictWriter(outputCSV, fieldnames=fieldNames)
    csvDictWriter.writeheader()

    for cellLine in outputDict:
        csvDictWriter.writerow(outputDict[cellLine])
