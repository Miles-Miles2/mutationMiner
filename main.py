import csv
import decimal

genes = set(['cellLineName'])

cellLines = set(())

cellLinesAndMutations = {}

nameToIDConversion = {}

radiosensitivityDict = {}

with open('radiosensitivityData.csv') as radiosensitivityData:
    rsdDictReader = csv.DictReader(radiosensitivityData)
    for row in rsdDictReader:
        radiosensitivityDict[row['cell_line']] = float(decimal.Decimal(row['2']))

with open('CellLineNameToCCLE_ID.csv') as NameToID:
    NameToIDDictReader = csv.DictReader(NameToID)


    for row in NameToIDDictReader:
        nameToIDConversion[row['DepMap_ID']] = row['stripped_cell_line_name']


with open('CCLE_mutations.csv') as mutationsAndSensitivity:
    csvDictReader = csv.DictReader(mutationsAndSensitivity)

    f = 0
    for row in csvDictReader:
        if f < 264/2:
            if nameToIDConversion[row['DepMap_ID']] in radiosensitivityDict.keys() and not row['DepMap_ID'] in cellLines:
                cellLines.add(row['DepMap_ID'])
                f += 1
                print(nameToIDConversion[row['DepMap_ID']])
                
        else:
            break




with open('CCLE_mutations.csv') as datacsv:
    csvDictReader = csv.DictReader(datacsv)

    for row in csvDictReader:
        protein = row['Protein_Change'][2:]
        if protein != "":
            if row['DepMap_ID'] in cellLines:
                if not row['Hugo_Symbol'] in genes:
                    genes.add(
                        row['Hugo_Symbol'])

cellLines = list(cellLines)

for cellLineName in cellLines:
    cellLinesAndMutations.update({cellLineName:{'cellLineName':cellLineName}})
genes = list(genes)


for cellLineName in cellLinesAndMutations:
    for geneName in genes:
        cellLinesAndMutations[cellLineName].update({geneName: 'notMutated'})

for cellLineName in cellLinesAndMutations:
    cellLinesAndMutations[cellLineName]['cellLineName'] = cellLineName


with open('CCLE_mutations.csv') as datacsv:
    csvDictReader = csv.DictReader(datacsv)

    for row in csvDictReader:
        protein = row['Protein_Change']
        if protein != "" and row['DepMap_ID'] in cellLines:
            cellLinesAndMutations[row['DepMap_ID']].update({row['Hugo_Symbol']: 'mutation'})
#row['Hugo_Symbol'], protein

print(len(cellLinesAndMutations))

with open(
    'mutationsCSV.csv',
    'w',
    newline=''

) as mutationsCSV:
    fieldnames = genes
    csvDictWriter = csv.DictWriter(mutationsCSV, fieldnames=fieldnames)
    csvDictWriter.writeheader()

    for cellLines in cellLinesAndMutations:
        csvDictWriter.writerow(cellLinesAndMutations[cellLines])

print("completed")

